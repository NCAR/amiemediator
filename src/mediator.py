import sys
from datetime import datetime
import logging
from logdumper import LogDumper
from amieclient import AMIEClient
from amieclient.packet.base import Packet as AMIEPacket
from misctypes import (DateTime, TimeUtil)
from miscfuncs import to_expanded_string
from retryingproxy import RetryingServiceProxy
from amieparms import get_packet_keys
from taskstatus import (State, TaskStatus)
from serviceprovider import (ServiceProvider, SPSession)
from spexception import *
from requests import ConnectionError
from transactionmanager import TransactionManager
from packetmanager import (ActionablePacket, PacketManager)
from packethandler import (PacketHandlerError, PacketHandler)

_config_defaults = {
    "amie_min_retry_delay": 60,
    "amie_max_retry_delay": 3600,
    "amie_retry_time_max": 14400,
    "amie_idle_loop_delay": 3600,
    "amie_busy_loop_delay": 60,
    "amie_reply_delay": 10,
    "snapshot_dir": "/tmp/amiemediator",
    "sp_absent_task_loop_delay": 21600,
    "sp_queued_task_loop_delay": 600,
    "sp_busy_task_loop_delay": 60,
    "sp_min_retry_delay": 60,
    "sp_max_retry_delay": 3600,
    "sp_retry_time_max": 14400,
    }

class WaitParms(object):
    def __init__(self, auto_update_delay, human_action_delay, idle_delay,
                 timeutil=None):
        self.timeutil = TimeUtil() if timeutil is None else timeutil
        self.auto_update_delay = auto_update_delay
        self.human_action_delay = human_action_delay
        self.idle_delay = idle_delay
        self.base_time = None
        self.target_time = None

    def set_base_time(self, datetime_val=None):
        if datetime_val is None:
            self.base_time = self.timeutil.now()
        else:
            self.base_time = datetime_val

    def set_target_time(self, expect_auto_response=False,
                        expect_human_action=False):
        if self.base_time == None:
            return self.timeutil.now()
        elif expect_auto_response:
            delay = self.auto_update_delay
        elif expect_human_action:
            delay = self.human_action_delay
        else:
            delay = self.idle_delay
        self.target_time = self.timeutil.future_time(delay, self.base_time)
        return self.target_time

    def set(self, base_time=None, expect_auto_response=False,
            expect_human_action=False):
        self.base_time = base_time
        if self.base_time == None:
            delay = 0
        elif expect_auto_response:
            delay = self.auto_update_delay
        elif expect_human_action:
            delay = self.human_action_delay
        else:
            delay = self.idle_delay
        self.target_time = self.timeutil.future_time(delay, self.base_time)
        return self.target_time

    def target_time(self):
        return self.target_time
    
    def wait_secs(self, currtime=None):
        if self.target_time is None:
            return 0
        if currtime is None:
            currtime = self.timeutil.now()
        wait = (self.target_time - currtime).total_seconds()
        return wait if wait >= 0 else 0

class AMIESession(RetryingServiceProxy):
    """Context Manager class for calling the AMIE client methods"""

    @classmethod
    def configure(cls, sp,
                  min_retry_delay, max_retry_delay, retry_time_max,
                  time_util=None):
        RetryingServiceProxy.configure(sp,min_retry_delay, max_retry_delay,
                                       retry_time_max, time_util)

class AMIEMediator(object):
    def __init__(self, config, amie_client, service_provider, timeutil=None):
        """Mediate interactions between AMIE and the local Service Provider

        An ``AMIEMediator`` instance collects packets from the AMIE server and
        ``TaskStatus`` objects from the local ``ServiceProvider``; it passes
        all this data to the :class:`~packetmanager.PacketManager` class to
        coordinate the running of tasks to service the AMIE packets.
        ``AMIEMediator`` controls timing - when and how often the AMIE server
        and ServiceProvider are queried.

        :param config: Configuration parameters; mostly timing related
        :type config: dict
        :param amie_client: An instance of AMIEClient; this talks to the AMIE
            service
        :type amie_client: AMIEClient
        :param service_provider: An instance of a ServiceProvider instance;
            this talks to the local site service
        :type service_provider: ServiceProvider
        """
        for attr in _config_defaults:
            val = config.get(attr,_config_defaults[attr])
            setattr(self,attr,val)

        self.logger = logging.getLogger(__name__)
        self.logdumper = LogDumper(self.logger)
        self.amie_client = amie_client
        self.site_name = self.amie_client.site_name
        AMIESession.configure(self.amie_client,
                              self.amie_min_retry_delay,
                              self.amie_max_retry_delay,
                              self.amie_retry_time_max)
        self.sp = service_provider
        self.timeutil = TimeUtil() if timeutil is None else timeutil
        SPSession.configure(service_provider,
                            self.sp_min_retry_delay,
                            self.sp_max_retry_delay,
                            self.sp_retry_time_max)

        self.sp_wait = WaitParms(
            auto_update_delay=self.sp_busy_task_loop_delay,
            human_action_delay=self.sp_busy_task_loop_delay,
            idle_delay=self.sp_absent_task_loop_delay,
            timeutil=self.timeutil)

        self.amie_wait = WaitParms(
            auto_update_delay=self.amie_reply_delay,
            human_action_delay=self.amie_busy_loop_delay,
            idle_delay=self.amie_idle_loop_delay,
            timeutil=self.timeutil)

        self.transaction_manager = TransactionManager(amie_wait_parms,
                                                      sp_wait_parms)
        self.packet_manager = PacketManager(self.site_name,
                                            self.snapshot_dir,
                                            self.transaction_manager)
        self.packet_logger = self.packet_manager.packet_logger
        PacketHandler.initialize_handlers()
        
        self.amie_packet_update_time = None
        self.task_query_time = None


    def run(self):
        """Service all active packets without waiting for updates

        The AMIE service is queried once for all active packets, and all
        packets are processed until there is nothing to do but wait for
        the local service provider.
        
        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderTemporaryError: if the request failed because of
            a temporary condition: these types of error are typically retried
            automatically, but will be raised here if too many retries fail
        """
        
        self._load_tasks(active=True)
        self._load_amie_packets()

        self.packet_manager.service_actionable_packets()

        return

    def run_loop(self):
        """Process all active packets in a loop

        Process packets until an exception is raised.
        
        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderRequestFailed: if the request is internally
            valid but could not be satisfied
        :raises ServiceProviderTemporaryError: if the request failed because of
            a temporary condition: these types of error are typically retried
            automatically, but will be raised here if too many retries fail
        """

        self._load_tasks()

        self._load_amie_packets()

        base_time = self.timeutil.now()

        (a_expect_repl, have_apkts, sp_expect_auto_upd, sp_expect_upd) = \
            self._service_actionable_packets()

        self.amie_wait.set(base_time, a_expect_repl, have_apkts)
        self.sp_wait.set(base_time, sp_expect_auto_upd, sp_expect_upd)
        
        while True:
            
            base_time = self.timeutil.now()

            if self.sp_wait.target_time is None or \
               self.sp_wait.target_time <= self.amie_wait.target_time:
                wait = int(self.sp_wait.wait_secs(base_time))
                self._load_tasks(wait=wait)

            else:
                a_wait = self.amie_wait.wait_secs(base_time)
                self.timeutil.sleep(a_wait)

                base_time = self.timeutil.now()
                self._load_amie_packets()
                self.amie_wait.set_base_time(base_time)

            base_time = self.timeutil.now()
            (a_expect_repl, have_apkts, sp_expect_auto_upd, sp_expect_upd) = \
                self._service_actionable_packets()

            self.amie_wait.set(base_time, a_expect_repl, have_apkts)
            self.sp_wait.set(base_time, sp_expect_auto_upd, sp_expect_upd)


    def run_loop_persistently(self):
        """Process all active packets in a loop, persistently

        Process packets until a serious exception is raised.
        
        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderRequestFailed: if the request is internally
            valid but could not be satisfied
        """
        
        while True:
            try:
                self.run_loop()
        
            except ServiceProviderTemporaryError:
                pass
            except ConnectionError:
                pass
            except Exception as err:
                raise err
        
    def _load_tasks(self, active=True, wait=None):
        with SPSession() as sp:
            tasks = sp.get_tasks(active=active, wait=wait,
                                 since=self.task_query_time)

        latest = 0.0 if not self.task_query_time else self.task_query_time
        for task in tasks:
            name = task['task_name']
            state = task['task_state']
            timestamp = float(task['timestamp'])
            if timestamp > latest:
                latest = timestamp
        self.task_query_time = None if latest == 0.0 else latest

        ntasks = len(tasks)
        m = f"Got {ntasks} tasks from Service Provider"
        if ntasks == 0:
            self.logger.debug(m)
        else:
            self.logger.info(m)

        self.transaction_manager.buffer_task_updates(tasks)
        self.packet_manager.refresh_tasks(tasks)
        # this calls pm.add_or_update_tasks(), which then calls
        # pm.add_or_update_task(), which is not called anywhere else.
        # pm.add_or_update_task() calls apacket_add_or_update_task(), which IS
        # called elsewhere
        

    def _load_amie_packets(self):
        currtime = self.timeutil.now();
        list_packets_parms = {
            'update_time_start': self.amie_packet_update_time,
            }
        with AMIESession() as amieclient:
            packets = amieclient.list_packets(**list_packets_parms).packets
            self.amie_packet_update_time = currtime

        npackets = len(packets)
        msg = f"Got {npackets} (unvalidated) packets from AMIE server"
        if npackets == 0:
            self.logger.debug(msg)
        else:
            self.logger.info(msg)
            
        serviceable_packets, obsolete_trids, itc_errs = \
            self._filter_out_unserviceable_amie_packets(packets)

        self.transaction_states.register_incoming_amie_packets(currtime, \
                                                          serviceable_packets)

        with SPSession() as sp:
            for trid in obsolete_trids:
                sp.clear_transaction(trid)
                self.packet_manager.purge_transaction(trid)
                self.transaction_states.purge(trid)

        expect_more_amie_packets = False
        for itc_err in itc_errs:
            sent_non_ITC = self._send_amie_packet(itc_err)
            if sent_non_ITC:
                expect_more_amie_packets = True

        self.packet_manager.refresh_packets(serviceable_packets)
        # This creates/updates ActionablePackets and merges in tasks
        # It also calls pm._purge_obsolete_task_transactions()

        return expect_more_amie_packets

    def _filter_out_unserviceable_amie_packets(self, amie_packets):
        ended_transactions = set()
        itc_error_replies = list()
        packets_to_service = []
        print("DEBUG in _filter_out_unserviceable_amie_packets")
        for packet in amie_packets:
            expected_replies=packet.__class__.expected_reply
            print("DEBUG packet_type="+packet.packet_type+" expected_replies="+to_expanded_string(expected_replies))

            disposition = None
            jid, atrid, aprid = get_packet_keys(packet)
            
            if packet.packet_type == "inform_transaction_complete" and \
               packet.remote_site_name == self.site_name:
                disposition = "Got ITC packet from AMIE - purging transaction"
                ended_transactions.add(atrid)
            elif packet.remote_site_name == self.site_name:
                err = self._get_invalid_packet_error(packet)
                if err is None:
                    packets_to_service.append(packet)
                    disposition = "Accepted incoming packet from AMIE"
                else:
                    disposition = "Rejecting invalid incoming packet from AMIE"
                    reply_packet = packet.reply_with_failure(message=err)
                    itc_error_replies.append(reply_packet)
            else:
                disposition = "Ignoring incoming packet from AMIE " +\
                    "with remote_site_name=" + packet.remote_site_name

            print("DEBUG   packet_type="+packet.packet_type+" site_name="+packet.remote_site_name+" disp="+disposition)
            self.packet_logger.debug(disposition + ":\n" + \
                                     packet.json(indent=2,sort_keys=True))
            self.logger.debug(disposition + ": " + atrid + ":" + aprid)
        return (packets_to_service, ended_transactions, itc_error_replies)

    def _get_invalid_packet_error(self, amie_packet):
        err = None
        if amie_packet.validate_data():
            missing = amie_packet.missing_attributes()
            if missing:
                err = "Required attributes are missing from packet: " + \
                    ",".join(missing)
        else:
            err = "validate_data() failed for packet"
        if err is not None:
            self.logdumper.info("Invalid packet (" + err + "):",amie_packet)
        return err


    def _service_actionable_packets(self):
        reply_packets = self.packet_manager.service_actionable_packets()
        expect_more_amie_packets = False
        for reply_packet in reply_packets:
            print("DEBUG service_actionable_packets for reply packet:\n" + \
                                     reply_packet.json(indent=2,sort_keys=True))
            sent_non_ITC = self._send_amie_packet(reply_packet)
            if sent_non_ITC:
                expect_more_amie_packets = True
        n_apackets = self.packet_manager.actionable_packet_count()
        (sp_expect_auto_upd, sp_expect_upd) = \
            self.packet_manager.get_expected_task_update_flags()
        
        return (expect_more_amie_packets,
                n_apackets > 0,
                sp_expect_auto_upd,
                sp_expect_upd)
        
    def _send_amie_packet(self, packet):
        """Send a packet to the AMIE server

        :return: True if the packet was NOT an "inform transaction complete"
            packet; this implies that we expect AMIE to send another packet
            for this transaction.
        """

        packet_type = packet.packet_type
        jid, atrid, aprid = get_packet_keys(packet)
        
        self.packet_logger.debug("Sending Reply Packet ("+packet_type+"):\n" +\
                                 packet.json(indent=2,sort_keys=True))
        self.logger.debug("Sending Reply Packet ("+packet_type+"): " + atrid + ":" + aprid)
        with AMIESession() as amieclient:
            self.amie_client.send_packet(packet)
        return (packet_type != 'inform_transaction_complete')
