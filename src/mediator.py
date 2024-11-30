import sys
from datetime import datetime
import logging
from logdumper import LogDumper
from amieclient import AMIEClient
from amieclient.packet.base import Packet as AMIEPacket
from misctypes import (DateTime, TimeUtil)
from miscfuncs import to_expanded_string
from retryingproxy import RetryingServiceProxy
from configdefaults import DFLT
from amieparms import get_packet_keys
from taskstatus import (State, TaskStatus)
from serviceprovider import (ServiceProvider, SPSession)
from spexception import *
from requests import ConnectionError
from loopdelay import (WaitParms, LoopDelay)
from transactionmanager import TransactionManager
from packetmanager import (ActionablePacket, PacketManager)
from packethandler import (PacketHandlerError, PacketHandler)


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
        :param timeutil: If non None, an instance of TimeUtil; this is passed
            in to make it easier to use a mock
        :type timeutil: TimeUtil or None
        """
        
        for attr in DFLT:
            val = config.get(attr,DFLT[attr])
            setattr(self,attr,val)

        self.logger = logging.getLogger(__name__)
        self.logdumper = LogDumper(self.logger)
        self.amie_client = amie_client
        self.site_name = self.amie_client.site_name
        AMIESession.configure(self.amie_client,
                              self.min_retry_delay,
                              self.max_retry_delay,
                              self.retry_time_max)
        self.sp = service_provider
        self.timeutil = TimeUtil() if timeutil is None else timeutil
        if service_provider:
            SPSession.configure(service_provider,
                                self.sp_min_retry_delay,
                                self.sp_max_retry_delay,
                                self.sp_retry_time_max)

        self.amie_wait = WaitParms(
            auto_update_delay=self.reply_delay,
            human_action_delay=self.busy_loop_delay,
            idle_delay=self.idle_loop_delay,
            timeutil=self.timeutil)

        self.transaction_manager = TransactionManager(self.amie_wait)
        self.packet_manager = PacketManager(self.snapshot_dir)
        self.packet_logger = self.packet_manager.packet_logger
        PacketHandler.initialize_handlers()
        
        self.amie_packet_update_time = None
        self.task_query_time = None


    def list_packets(self):
        """List all packets for our site

        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderTemporaryError: if the request failed because of
            a temporary condition: these types of error are typically retried
            automatically, but will be raised here if too many retries fail
        :return: list of ActionablePacket
        """
        
        with AMIESession() as amieclient:
            packets = amieclient.list_packets().packets
        for packet in packets:
            print(to_expanded_string(packet))


    def fail_transaction(self, trid):
        """Set the status of the indicated transacton to Failed.

        :param trid: The AMIE transaction ID
        :type trid: str
        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderTemporaryError: if the request failed because of
            a temporary condition: these types of error are typically retried
            automatically, but will be raised here if too many retries fail
        :return: list of ActionablePacket
        """

        response = None
        print("Failing transaction " + trid + ":")
        with AMIESession() as amieclient:
            response = self.amie_client.set_transaction_failed(trid)

        if response:
            print("Status code = " + str(response.status_code))


    def run(self) -> list:
        """Service all active packets without waiting for updates

        The AMIE service is queried once for all active packets, and all
        packets are processed until there is nothing to do but wait for
        the local service provider.
        
        :raises ServiceProviderError: if an internal error was encountered
        :raises ServiceProviderTemporaryError: if the request failed because of
            a temporary condition: these types of error are typically retried
            automatically, but will be raised here if too many retries fail
        :return: list of ActionablePacket
        """

        self._load_tasks()

        apackets = self._load_amie_packets()
        self._flush_amie_packets()

        apackets = self._service_actionable_packets(apackets)
        self._flush_amie_packets()

        return apackets

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

        #
        # Call run() outside the main loop to initialize transactionmanager;
        # this calls _load_tasks() and _load_amie_packets() unconditionally,
        # and retrieves ALL known active tasks and packets. When we enter the
        # loop, calls to _load_tasks() and _load_amie_packets() will include
        # parameters to retrieve only updated tasks/packets.
        #
        apackets = self.run()

        pause_max = int(self.pause_max)
        
        previous_wait_secs = 0
        
        while True:

            # How long we wait before querying AMIE again depends on whether
            # we just sent AMIE a packet, and whether any packets are being
            # worked on locally by the ServiceProvider. In any case we don't
            # want to pause more than self.pause_max seconds.
            
            loop_delay = self.transaction_manager.get_loop_delay()
            wait_secs = loop_delay.wait_secs()
            self.logger.debug("loop_delay: base=" +\
                              str(loop_delay.get_base_time()) +\
                              " target=" + str(loop_delay.get_target_time()) +\
                              " wait_secs=" + str(wait_secs))
            if wait_secs:
                if wait_secs > pause_max:
                    wait_secs = pause_max
                # Whenever we increase the time we are waiting, ramp up to
                # the calculated wait time; e.g. if we had a short wait because
                # we were expecting a reply from AMIE, but we are no longer
                # expecting anything from AMIE, there is still a chance that
                # there is a cluster of requests, so we don't want to wait too
                # long for them
                if wait_secs > previous_wait_secs:
                    ramped_wait_secs = max(previous_wait_secs * 2, 4)
                    if ramped_wait_secs < wait_secs:
                        wait_secs = ramped_wait_secs
            
            if self.transaction_manager.have_actionable_packets():
                self._load_tasks(wait=wait_secs)
            elif wait_secs:
                self.logger.debug("Sleeping " + str(wait_secs) + " sec")
                self.timeutil.sleep(wait_secs)
                
            previous_wait_secs = wait_secs if wait_secs else 0

            apackets = self._load_amie_packets()
            self._flush_amie_packets()

            if apackets:
                apackets = self._service_actionable_packets(apackets)
                self._flush_amie_packets()
                

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
        
    def _load_tasks(self, active=True, wait=None) -> int:
        m = "Calling ServiceProvider.get_tasks(active=" + str(active) +\
            ", wait=" + str(wait) + ", since=" + str(self.task_query_time) + ")"
        self.logger.debug(m)
        
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
        self.task_query_time = None if latest == 0.0 else int(latest)

        ntasks = len(tasks)
        m = f"Got {ntasks} tasks from Service Provider"
        if ntasks == 0:
            self.logger.debug(m)
        else:
            self.logger.info(m)

        self.transaction_manager.buffer_task_updates(tasks)
        return ntasks

    def _load_amie_packets(self) -> list:
        packets = None
        currtime = self.timeutil.now();
        all_packets = self.amie_packet_update_time is None
        list_packets_parms = {
            'update_time_start': self.amie_packet_update_time,
            }
        m = "Calling amieclient.list_packets() with update_start_time=" +\
            str(self.amie_packet_update_time)
        self.logger.debug(m)
        with AMIESession() as amieclient:
            packets = amieclient.list_packets(**list_packets_parms).packets
            self.amie_packet_update_time = currtime

        npackets = len(packets)
        msg = f"Got {npackets} (unvalidated) packets from AMIE server"
        if npackets == 0:
            self.logger.debug(msg)
        else:
            self.logger.info(msg)

        packets = self._filter_packets(packets)

        if all_packets:
            inactive_trids = self.transaction_manager.get_transaction_ids()
        else:
            inactive_trids = set()
            
        for packet in packets:
            itc_info = self._get_itc_info(packet)
            log_tag = self._get_packet_log_tag(packet, itc_info)

            jid, atrid, pid = get_packet_keys(packet)

            inactive_trids.discard(atrid)
            msg = self.transaction_manager.buffer_incoming_amie_packet(currtime,
                                                                       packet)
            if msg is None:
                # saw this packet already
                continue
            
            self.packet_logger.debug(msg + " " + log_tag + ":\n" + \
                                     packet.json(indent=2,sort_keys=True))
            self.logger.debug(msg + ": " + log_tag)

        if inactive_trids:
            self._purge_obsolete_transactions(inactive_trids)

        return self.transaction_manager.get_actionable_packets()

    def _filter_packets(self, packets):
        packets_for_us = list()
        for packet in packets:
            if packet.remote_site_name == self.site_name:
                packets_for_us.append(packet)
            else:
                disposition = "Ignoring incoming packet from AMIE " +\
                    "with remote_site_name=" + packet.remote_site_name
                self.packet_logger.debug(disposition + ":\n" + \
                                         packet.json(indent=2,sort_keys=True))
        return packets_for_us
            

    def _purge_obsolete_transactions(self, trids):
        for atrid in trids:
            self._purge_obsolete_transaction(atrid)

    def _purge_obsolete_transaction(self, atrid):
        with SPSession() as sp:
            self.logger.debug("Clearing transaction "+atrid)
            sp.clear_transaction(atrid)
            apackets = self.transaction_manager.get_actionable_packets(atrid)
            self.packet_manager.purge_actionable_packets(apackets)
            self.transaction_manager.purge(atrid)
        
    def _flush_amie_packets(self):
        packets = self.transaction_manager.get_outgoing_amie_packets()
        for packet in packets:
            self._send_amie_packet(packet)

    def _service_actionable_packets(self, apackets):
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Servicing ActionablePackets:")
            for apacket in apackets:
                self.logger.debug("    " + apacket.mk_name())
        reply_packets = self.packet_manager.service_actionable_packets(apackets)

        for reply_packet in reply_packets:
            self.transaction_manager.buffer_outgoing_amie_packet(reply_packet)

        apackets = self.transaction_manager.get_actionable_packets()
        
    def _send_amie_packet(self, packet):
        """Send a packet to the AMIE server

        :return: True if the packet was NOT an "inform transaction complete"
            packet; this implies that we expect AMIE to send another packet
            for this transaction.
        """

        itc_info = self._get_itc_info(packet)
        log_tag = self._get_packet_log_tag(packet, itc_info)
        
        self.packet_logger.debug("Sending Reply Packet ("+log_tag+"):\n" +\
                                 packet.json(indent=2,sort_keys=True))
        self.logger.debug("Sending Reply Packet "+log_tag)

        with AMIESession() as amieclient:
            self.amie_client.send_packet(packet)

        if itc_info:
            jid, atrid, pid = get_packet_keys(packet)
            self._purge_obsolete_transaction(atrid)

    def _get_itc_info(self, packet):
        packet_type = packet.__class__._packet_type
        if packet_type == 'inform_transaction_complete':
            info = " " + str(packet.StatusCode)
            if packet.Message:
                info = info + " (" + packet.Message + ")"
            return info
        return None
        
    def _get_packet_log_tag(self, packet, itc_info):
        term = ": " + itc_info if itc_info else ''
        jid, atrid, pid = get_packet_keys(packet)
        packet_type = packet.__class__._packet_type
        return atrid + ":" + pid + " " + packet_type + term
        
