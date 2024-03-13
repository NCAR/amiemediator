import logging
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from logdumper import LogDumper
from datetime import datetime
from amieclient import AMIEClient
from amieclient.packet.base import Packet as AMIEPacket
from misctypes import DateTime
from amieparms import get_packet_keys
from loopdelay import (WaitParms, LoopDelay)

PACKET_TYPE2EXPECTED_REPLY_TYPES = dict();

def get_expected_reply_types(packet):
    packet_type = packet.packet_type
    expected_types = PACKET_TYPE2EXPECTED_REPLY_TYPES.get(packet_type,None)
    if expected_types is None:
        expected_types = set()
        packet_class = initial_packet.__class__
        expected_reply = packet_class._expected_reply
        for t in expected_reply:
            if isinstance(t, str):
                expected_types.add(str)
            elif isinstance(t, dict):
                expected_types.add(t['type'])
            else:
                raise TypeError("packet class "+packet_class.__name__+\
                        "._expected_reply list member has unexpected type: "+\
                        t.__class__.__name__)
        PACKET_TYPE2EXPECTED_REPLY_TYPES[packet_type] = expected_types
    return expected_types

class Transaction(object):
    def __init__(self, atrid, amie_wait_parms, task_wait_parms):
        """The state of an AMIE "transaction"

        :param atrid: AMIE transaction ID
        :type atrid: str
        :param amie_wait_parms: Poll wait parameters for AMIE 
        :type packet: WaitParms
        :param amie_wait_parms: Poll wait parameters for the ServiceProvider
        :type packet: WaitParms
        """

        self.atrid = atrid
        self.amie_loop_delay = LoopDelay(amie_wait_parms)
        self.task_loop_delay = LoopDelay(task_wait_parms)
        self.active_packet_type = None
        self.next_expected_types = None
        self.amie_packet = None
        self.amie_packet_incoming = True
        self.tasks = dict()

    def register_amie_query(self, querytime):
        self.waiting_for_amie = False
        self.amie_loop_delay.set_base_tme(querytime)

    def buffer_incoming_amie_packet(self, packet):
        """Adjust transaction state for incoming AMIE packet and save it

        :param packet: Incoming packet
        :type packet: amieclient.packet.base.Packet
        """

        packet_type = packet.packet_type
        if self.next_expected_types is not None:
            if packet_type not in self.next_expected_types:
                err = "Unexpected packet type for transaction "+self.atrid+\
                    ": Expecting ["+' or '.join(self.next_expected_types)+"],"+\
                    " got "+packet_type
                reply_packet = packet.reply_with_failure(message=err)

                self.active_packet_type = "inform_transaction_complete"
                self.next_expected_types = []
                self.amie_packet = reply_packet
                self.amie_packet_incoming = False
            else:
                self.active_packet_type = packet_type
                self.next_expected_types = get_expected_reply_types(packet)
                self.amie_packet = packet
                self.amie_packet_incoming = True

    def get_incoming_amie_packet(self) -> AMIEPacket:
        """Return the buffered incoming AMIE packet"""

        if self.amie_packet_incoming:
            return self.amie_packet
        return None

    def buffer_outgoing_amie_packet(self, packet):
        """Adjust transaction state for outgoing AMIE packet and save it
        
        :param packet: Outgoing packet
        :type packet: amieclient.packet.base.Packet
        """

        self.active_packet_type = packet.packet_type
        self.next_expected_types = get_expected_reply_types(packet)
        self.amie_packet = packet
        self.amie_packet_incoming = False

    def get_outgoing_amie_packet(self) -> AMIEPacket:
        """Return the buffered outgoing AMIE packet"""

        if not self.amie_packet_incoming:
            return self.amie_packet
        return None

    def add_or_update_task(self, aprid, task_status):
        target_time = self.task_loop_delay.target_time()
        state = task_status['task_state']
        # WORK HERE tasklist.find_active_task()
        candidate_target_time
        tslist = self.tasks.get(aprid, None)
        if tslist is not None:
            tslist.put(task_status)
        else:
            tslist = TaskStatusList(task_status)
            self.tasks[aprid] = tslist

    def get_tasks(self, aprid) -> TaskStatusList:
        return self.tasks.get(aprid, None)

class TransactionManager(object):
    
    def __init__(self, amie_wait_parms, task_wait_parms):
        """Maintain state for all AMIE transactions

        For each transaction, keep track of the next expected action and how
        soon we should poll for update, either from AMIE or the ServiceProvider

        :param amie_wait_parms: Polling parameters for AMIE
        :type amie_wait_parms: WaitParms
        :param amie_wait_parms: Polling parameters for the ServiceProvider
        :type amie_wait_parms: WaitParms
        
        
        WORK HERE
        have the mediator use this class as an intermediary to packetmanager:
        send all tasks to this class, send all packets to this class,
        and have packetmanager pull them instead of having mediator call
        pm.refresh_tasks() and pm.refresh_packets()

        handler.work() will return an AMIE packet if it has no more to do. Once
        a packet has been retrieved from a handler, we do not want to call the
        handler again. However, we want to save the packet so it can be resent
        until we get confirmation that AMIE has received it.
        
        """

        self.amie_wait_parms = amie_wait_parms
        self.task_wait_parms = task_wait_parms

        self.transactions = dict()
        self.incoming_amie_packet_transactions = list()

    def buffer_incoming_amie_packets(self, querytime, packets):
        """Buffer packets from an AMIE query and adjust transaction states

        Inform all transactions that AMIE packets have just been received;
        pass individual packets to their transaction objects to update the
        transaction state; save all packets for the further processing: see
        get_amie_packets().

        :param querytime: The time the query was made to AMIE
        :type querytime: DateTime
        :param packets: List of serviceble AMIE packets just received (can be
            empty)
        :type packets: list of amieclient.packet.base.Packet
        """
        
        for transaction in self.transactions.value():
            transaction.register_amie_query(querytime)

        for packet in packets:
            transaction = self.get_transaction(packet)
            transaction.buffer_incoming_amie_packet(packet)
            self.incoming_amie_packet_transactions.append(packet)

    def get_incoming_amie_packets(self):
        amie_packets = list();
        for transaction in self.incoming_amie_packet_transactions:
            packet = transaction.get_incoming_amie_packet()
            if packet is not None:
                amie_packets.append(packet)
        self.incoming_amie_packet_transactions.clear()

    def buffer_outgoing_amie_packet(self, packet):
        """Adjust transaction state for outgoing packet and buffer the packet

        :param packet: A serviceble AMIE packets just received
        :type packet: amieclient.packet.base.Packet
        """
        jid, atrid, aprid = get_packet_keys(packet)
        transaction = transactions[atrid]
        transaction.buffer_outgoing_amie_packet(packet)

    def load_task_updates(self, tasks):
        for task in tasks:
            jid, atrid, aprid = get_packet_keys(packet)
            transaction = self._get_transaction_by_id(aprid)
            transaction.put_task_update(aprid,task)

    def add_or_update_task(self, task):
        jid, atrid, aprid = get_packet_keys(task)
        transaction = self._get_transaction_by_id(atrid)
        transaction.add_or_update_task(aprid, task)

    def get_tasks(self, atrid, aprid) -> TaskStatusList:
        transaction = self._get_transaction_by_id(atrid)
        return transaction.get_tasks(aprid)

    def purge(self, atrid):
        self.transactions.pop(atrid,None)

    def _get_transaction(self, packet_or_task_status):
        jid, atrid, aprid = get_packet_keys(packet)
        return self._get_transaction_by_id(atrid)

    def _get_transaction_by_id(self, atrid):
        transaction = transactions.get(atrid, None)
        if not transaction:
            transaction = Transaction(self.amie_wait_parms,self.task_wait_parms)
            transactions[atrid] = transaction
        return transaction
    
    def _register_incoming_amie_packet(self, packet):
        transaction = self._get_transaction(packet)
        transaction.register_incoming_amie_packet(packet)
    
