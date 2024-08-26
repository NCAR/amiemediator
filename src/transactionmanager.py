import logging
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from logdumper import LogDumper
from datetime import datetime
from amieclient import AMIEClient
from amieclient.packet.base import Packet as AMIEPacket
from misctypes import DateTime
from amieparms import (get_packet_keys, parse_atrid)
from taskstatus import (TaskStatus, TaskStatusList)
from loopdelay import (WaitParms, LoopDelay)
from actionablepacket import ActionablePacket

class Transaction(object):
    def __init__(self, amie_wait_parms, atrid):
        """The state of an AMIE "transaction"

        :param amie_wait_parms: Poll wait parameters for AMIE 
        :type packet: WaitParms
        :param atrid: AMIE transaction ID
        :type atrid: str
        """

        self.loop_delay = LoopDelay(amie_wait_parms)

        self.atrid = atrid
        self.amie_packet = None
        self.amie_packet_incoming = True
        self.actionable_packet = None

        # keys for actionable_packets and dangling_tasks are packet_ids
        self.dangling_tasks = dict()

    def transaction_id(self):
        return self.atrid
    
    def buffer_task(self, pid, task_status):
        """Add or update an associated task

        :param pid: AMIE packet_id
        :type pid: str
        :param task_status: task from the service provider
        :type task_status: TaskStatus
        """
       
        # Normally, we retrieve the TaskStatusList from our ActionablePacket,
        # but when we start up, it is possible we will be given tasks before
        # we see the associated packet and create an ActionablePacket. In
        # this case, maintain the TaskStatusList separately until we can
        # move it to the ActionablePacket

        if self.actionable_packet is not None:
            tslist = self.actionable_packet.get_tasks()
        else:
            tslist = self.dangling_tasks.get(pid, None)
            if tslist is None:
                tslist = TaskStatusList(task_status)
                self.dangling_tasks[pid] = tslist
            
        tslist.put(task_status)
        
    def buffer_incoming_amie_packet(self, querytime, packet) \
        -> (ActionablePacket, str):
        """Adjust transaction state for incoming AMIE packet and save it

        If the packet has not been seen before, the packet is validated and
        a new ActionablePacket is created. If validation fails, the
        method returns (None, errmsg). If validation succeeds, the method
        returns (apacker, None).

        If the packet HAS been seen before, the method returns (None, None).

        If a new valid packet is seen, the LoopDelay object for the transaction
        is updated. It is also updated if the packet has been seen before and
        the target time has passed.

        :param querytime: Time AMIE server was queried for packets (should
            be very recently)
        :type querytime: datetime
        :param packet: Incoming packet
        :type packet: amieclient.packet.base.Packet
        :return: (ActionablePacket, None) or (None, None) or (None, errmsg)
        """

        actionable_packet = None
        calculate_new_target_time = False
        if self._is_amie_packet_new(packet):
            err = self._get_invalid_packet_error(packet)
            if err:
                return (None, err)
            jid, atrid, pid = get_packet_keys(packet)
            ptype = packet.__class__._packet_type
            self.amie_packet = packet
            tasks = self.dangling_tasks.get(pid, None)
            actionable_packet = ActionablePacket(packet, tasks)
            self.actionable_packet = actionable_packet
            self.amie_packet_incoming = True
            calculate_new_target_time = True
        elif self.loop_delay.get_target_time() < querytime:
            calculate_new_target_time = True

        if calculate_new_target_time:
            self.loop_delay.calculate_target_time(querytime,
                                                  expect_human_action=True)
        return (actionable_packet, None)
    
    def get_actionable_packet(self) -> ActionablePacket:
        """Return the current ActionablePacket for the transaction
        :return: ActionablePacket or None
        """

        return self.actionable_packet

    def buffer_outgoing_amie_packet(self, packet):
        """Adjust transaction state for outgoing AMIE packet and save it
        
        :param packet: Outgoing packet
        :type packet: amieclient.packet.base.Packet
        """

        print("DEBUG Transaction.buffer_outgoing_amie_packet")
        print("DEBUG  packet="+to_expanded_string(packet))
        
        if not self._is_amie_packet_new(packet):
            return
        jid, atrid, pid = get_packet_keys(packet)
        self.amie_packet = packet
        self.actionable_packet = None
        self.amie_packet_incoming = False

        # We want to keep the packet buffered so that we can resend it if we
        # don't get some indication from the AMIE server that the packet was
        # received. But we want to hold off on resending until a suitable
        # amount of time has passed. The loop_delay's target_time will
        # indicate when we can retry. We initialize it to the current time
        # so that newly buffered packets will be sent straight away.
        self.loop_delay.calculate_target_time(immediate=True)

    def get_outgoing_amie_packet(self, now=None) -> AMIEPacket:
        """Return the buffered outgoing AMIE packet if it is ready to be sent

        :param now: The current time, provided by the caller. The current time
            is used to determine whether it is time to resend a buffered
            packet
        :type now: datetime or None
        :return: AMIEPacket ready to be sent, or None
        """

        if self.amie_packet_incoming:
            return None
        if now is None:
            now = self.loop_delay.now()

        if self.loop_delay.get_target_time() > now:
            # it's not time yet to resend the packet
            return None

        self.loop_delay.calculate_target_time(now, expect_auto_response=True)
        return self.amie_packet

    def get_tasks(self, pid) -> TaskStatusList:
        """Return the TaskStatusList for the current packet

        :param pid: packet_id
        :type pid: int or str
        :return: TaskStatusList, or None if there is no active packet
        """

        if self.actionable_packet is not None:
            return self.actionable_packet.get_tasks()
        else:
            return self.dangling_tasks.get(str(pid), None)

    def have_outgoing_packet(self):
        return not self.amie_packet_incoming

    def _is_amie_packet_new(self, packet) -> bool:
        tpacket = self.amie_packet
        if not tpacket or \
           tpacket.originating_site_name != packet.originating_site_name or \
           tpacket.local_site_name != packet.local_site_name or \
           tpacket.remote_site_name != packet.remote_site_name or \
           tpacket.transaction_id != packet.transaction_id or \
           tpacket.packet_rec_id != packet.packet_rec_id or \
           tpacket.__class__._packet_type != packet.__class__._packet_type:
            return True
        return False

    def _get_invalid_packet_error(self, packet):
        err = None
        if packet.validate_data():
            missing = packet.missing_attributes()
            if missing:
                err = "Required attributes are missing from incoming packet: " \
                    + ",".join(missing)
        else:
            err = "packet.validate_data() failed for incoming packet"
        return err


class TransactionManager(object):
    
    def __init__(self, amie_wait_parms):
        """Maintain state for all AMIE transactions

        For each transaction, keep track of the current packet, whether
        it is incoming or outgoing, related tasks, and how soon the next
        update can reasonable be expected (to determine loop timing).

        :param amie_wait_parms: Polling parameters for AMIE
        :type amie_wait_parms: WaitParms
        :param timeutil: TimeUtil object (can be a mock for testing)
        :type amie_wait_parms: Timeutil
        """

        self.amie_wait_parms = amie_wait_parms
        self.timeutil = amie_wait_parms.get_timeutil()

        # Keys for transactions and actionable_packets are AMIE transaction ID
        # strings. Values for transactions are Transaction instances. Values
        # for actionable_packets are dicts that map packet_ids to
        # ActionablePacket instances
        #
        self.transactions = dict()
        self.actionable_packets = dict()

    def get_transaction_ids(self) -> set:
        """Return all known transaction IDs as a set"""
        return set(self.transactions.keys())
    
    def add_or_update_task(self, task):
        """Buffer the given task with its associated transaction

        :param task: task
        :type task: TaskStatus
        """
        
        jid, atrid, pid = get_packet_keys(task)
        
        transaction = self._get_transaction_by_id(atrid)
        transaction.buffer_task(pid, task)
    
    def buffer_task_updates(self, tasks) -> int:
        """Buffer latest TaskStatus objects from the ServiceProvider

        :param tasks: Collection of task updates
        :type tasks: list of TaskStatus
        """

        for task in tasks:
            self.add_or_update_task(task)

    def get_tasks(self, atrid, pid) -> TaskStatusList:
        """Get all tasks associated with a Packet

        :param atrid: An AMIE transactionID
        :type atrid: str
        :param pid: A packet_rec_id
        :type pid: str
        :return: TaskStatisList or None if the packet ID is unknown
        """
        
        transaction = self._get_transaction_by_id(atrid)
        return transaction.get_tasks(pid)

    def buffer_incoming_amie_packet(self, querytime, packet) -> str:
        """Buffer packet from an AMIE query and adjust transaction state

        Pass a packet to its transaction object to update the
        transaction state. If the incoming packet can be immediately
        acted upon with a reply packet, buffer the reply packet (see
        get_outgoing_amie_packets()). Otherwise, buffer the incoming packet
        for further processing (see get_incoming_amie_packets()).

        :param querytime: The time the query was made to AMIE
        :type querytime: datetime
        :param packet: AMIE packet just received
        :type packet: amieclient.packet.base.Packet
        :return: Message describing disposition of packet
        """
        
        transaction = self._get_transaction(packet)
        atrid = transaction.transaction_id()

        disposition = None

        
        packet_type = packet.__class__._packet_type
        if packet_type == "inform_transaction_complete":
            # Not sure if this is right.
            # Code in amieclient/examples/process_packets.py suggests
            # we should always reply to an ITC with a success ITC, but then
            # how does it ever end?
            # Would an incoming ITC always be for a failure?
            reply_packet = ActionablePacket.create_reply(packet)
            reply_packet.StatusCode = 'Success'
            reply_packet.DetailCode = '1'
            reply_packet.Message = 'OK'

            transaction.buffer_outgoing_amie_packet(reply_packet)
            self.actionable_packets.pop(atrid, None)
            disposition = "Handled incoming packet from AMIE"

        else:
            (apacket, err) = \
                transaction.buffer_incoming_amie_packet(querytime, packet)

            if err is not None:
                reply_packet = \
                    ActionablePacket.create_failure_reply(packet, message=err)
                transaction.buffer_outgoing_amie_packet(reply_packet)
                self.actionable_packets.pop(atrid, None)
                disposition = err

            elif apacket is None:
                # Not a new packet
                return None
            else:
                disposition = "Accepted/buffered incoming packet from AMIE"
                self.actionable_packets[atrid] = apacket

        return disposition

    def have_actionable_packets(self) -> bool:
        """Return True if there are ActionablePacket objects, False otherwise
        """

        return True if self.actionable_packets else False

    def get_actionable_packets(self, atrid=None) -> list:
        """Retrieve ActionablePacket list

        An ActionablePacket is a dictionary-like object that encapsulates
        an AMIE packet and its associated tasks and state.

        :param atrid: If not None, a target transaction ID
        :type atrid: str
        :return: list of ActionablePacket
        """

        if not atrid:
            return list(self.actionable_packets.values())
        
        apackets = list()
        for apacket in self.actionable_packets.values():
            if apacket['amie_transaction_id'] == atrid:
                apackets.append(apacket)
            
        return apackets

    def buffer_outgoing_amie_packet(self, packet):
        """Adjust transaction state for outgoing packet and buffer the packet
        
        :param packet: A serviceble AMIE packets just received
        :type packet: amieclient.packet.base.Packet
        """

        print("DEBUG TransactionManager.buffer_outgoing_amie_packet")
        jid, atrid, pid = get_packet_keys(packet)
        transaction = self.transactions[atrid]
        transaction.buffer_outgoing_amie_packet(packet)
        self.actionable_packets.pop(atrid, None)

    def get_outgoing_amie_packets(self) -> list:
        """Get buffered outgoing packets ready to be sent

        :return: list of amieclient.packet.base.Packet
        """

        now = self.timeutil.now()
        sendable_packets = list();
        for transaction in self.transactions.values():
            packet = transaction.get_outgoing_amie_packet(now)
            if packet is not None:
                sendable_packets.append(packet)

        return sendable_packets

    def purge(self, atrid):
        """Purge all state for the indicated transaction

        :param atrid: AMIE transaction ID
        :type atrid: str
        """

        self._purge_actionable_packets(atrid)
        self.transactions.pop(atrid,None)

    def get_loop_delay(self) -> LoopDelay:
        """Return LoopDelay that shows how long to wait before querying AMIE"""

        loop_delay = LoopDelay(self.amie_wait_parms)
        now = self.timeutil.now()
        
        # The following sets target_time to latest possible
        loop_delay.calculate_target_time(now)

        earliest_target_time = loop_delay.get_target_time()

        for transaction in self.transactions.values():
            # Each transaction has a LoopDelay object (loop_delay) with a
            #  target_time value.
            # For a transaction with an outgoing packet, the target_time is when
            #  to resend if we get no acknowledgement that the send packet
            #  was processed by AMIE.
            # For other transactions, the target_time is the soonest we want
            #  to query AMIE for new packets; we want to query more often if
            #  the ServiceProvider has active tasks. Also, if there are active
            #  tasks we want to delay by calling ServiceProvider.get_tasks()
            #  with the "wait" parameter, but otherwise we just want to sleep.
            transaction_target_time = transaction.loop_delay.get_target_time()
            if earliest_target_time > transaction_target_time:
                earliest_target_time = transaction_target_time
                
        loop_delay.set_target_time(earliest_target_time)
        return loop_delay

        
    def _get_transaction(self, packet_or_task_status):
        jid, atrid, pid = get_packet_keys(packet_or_task_status)
        return self._get_transaction_by_id(atrid)

    def _get_transaction_by_id(self, atrid):
        transaction = self.transactions.get(atrid, None)
        if not transaction:
            transaction = Transaction(self.amie_wait_parms, atrid)
            self.transactions[atrid] = transaction
        return transaction

    def _purge_actionable_packets(self, atrid):
        self.transactions.pop(atrid,None)
        
    
