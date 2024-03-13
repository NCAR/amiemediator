import logging
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from logdumper import LogDumper
from datetime import datetime
from snapshot import Snapshots
from amieclient import AMIEClient
from amieclient.packet.base import Packet as AMIEPacket
from misctypes import DateTime
from amieparms import get_packet_keys
from taskstatus import (State, TaskStatus, TaskStatusList)
from actionablepacket import ActionablePacket
from packethandler import (PacketHandlerError, PacketHandler)
from spexception import (ServiceProviderTimeout, ServiceProviderRequestFailed)
from transactionstates import TransactionStates
                         

SNAPSHOT_DFLT_KEYS = [
    'job_id',
    'packet_type',
    'amie_packet_timestamp',
    'amie_transaction_id',
    'amie_packet_rec_id',
    'timestamp',
    'tasks'
]
SNAPSHOT_EXCLUDE_KEYS = [
    'amie_packet'
    ]
SNAPSHOT_DFLT_TASK_KEYS = [
    'task_name',
    'task_state',
    'timestamp',
    'products'
]

        
class PacketManager(object):

    def __init__(self, site_name, snapshot_dir, transaction_states):
        """Coordinate the running of tasks to service AMIE packets

        AMIE packets are converted to ``ActionablePacket`` objects, which are
        associated with tasks (more specifically with
        :class:`~taskstatus.TaskStatus` objects. The ``PacketManager``
        maintains maps of ``ActionablePacket`` objects and ``TaskStatus``
        objects and can cross-reference between the two.

        Snapshots:
        
        In addition to an in-memory dictionary of ``ActionablePacket`` objects,
        PacketManager maintains a directory with ActionablePacket "snapshots"
        that are updated as the objects change. Snapshots are files containing
        JSON-serialized ``ActionablePacket`` data. Snapshots are meant to
        facilitate external monitoring of the AMIE mediator state. In
        particular, snapshots are NOT used by the mediator itself to remember
        the state of AMIE packets or ``ServiceProvider`` tasks; all persistent
        state of this kind is the responsibility of the AMIE server and the
        local ``ServiceProvider`` implementation.
        
        Snapshots initially contain only the keys in
        :data:~packetmanager.SNAPSHOT_DFLT_KEYS` and not in
        :data:~packetmanager.SNAPSHOT_EXCLUDE_KEYS`. Updated snapshots contain
        these keys plus any keys that were not in the original
        ``ActionablePacket``. When all tasks for a packet are complete and an
        AMIE reply packet can be created, the snapshot is updated to contain
        the complete ``ActionablePacket``.

        :param site_name: the local site name
        :type site_name: str
        :param snapshot_dir: the name of the directory for apacket snapshots
        :type site_name: str
        :param transaction_states: Object for tracking state of transactions
        :type site_name: TransactionStates
        
        """

        self.site_name = site_name
        self.packet_logger = logging.getLogger("amiepackets")
        self.logger = logging.getLogger(__name__)
        self.logdumper = LogDumper(self.logger)
        # self.snapshot_data contains current data from ActionablePackets,
        # indexed by apacket.mk_name().
        # self.initial_snapshot_data contains complete serialized
        # ActionablePackets, also index by apacket.mkname(); it is used to
        # limit snapshot_data to attributes that are modified.
        self.snapshot_data = {}
        self.initial_snapshot_data = {}

        self.snapshots = Snapshots(snapshot_dir, 'w')

        self.transaction_states = transaction_states

        # TaskStatusLists indexed by job_id. It is possible for a TaskStatusList
        # to temporarily exist without an ActionablePacket, but once an
        # ActionablePacket with the same job_id exits, self.tasks[job_id] will
        # reference the same TaskStatusList as apacket['tasks']
        self.tasks = {}
        
        # ActionablePackets indexed by (amie_transaction_id,amie_packet_rec_id)
        self.actionable_packets = {}

        PacketHandler.initialize_handlers()

    def actionable_packet_count(self):
        return len(self.actionable_packets)

    
    def refresh_packets(self, packets):
        """Add/update the manager's set of packets from AMIE

        If the AMIE packet does not have a corresponding ActionablePacket
        object, create one. If any extant tasks no longer has a corresponding
        AMIE packet, purge it. In additon, ensure snapshot files are up-to-date.

        :param packets: List of serviceable AMIE packets
        :type packets: list
        """

        for packet in packets:
            jid, atrid, aprid = get_packet_keys(packet)

            packet_tasks = self.tasks.get(jid,None)

            key = (atrid, aprid)
            if key in self.actionable_packets:
                apacket = self.actionable_packets[key]
                apacket.update(packet, packet_tasks)
                self.tasks[jid] = apacket['tasks']
                self._update_snapshot(apacket)
            else:
                apacket = ActionablePacket(packet, packet_tasks)
                self.logdumper.debug("Created ActionablePacket:",apacket)
                self.actionable_packets[key] = apacket
                self._add_apacket_to_snapshots(apacket)

        self._purge_obsolete_task_transactions()
            
    def refresh_tasks(self, tasks):
        """Add/update TaskStatus objects from the ServiceProvider

        :param tasks: The TaskStatus objects to add/update
        :type tasks: list
        """

        for task in tasks:
            self.add_or_update_task(task)
        
    def add_or_update_task(self, task_status):
        """Add/update a task in the appropriate ActionablePacket object

        :param task_status: The task
        :type task_status: TaskStatus
        """
        
        jid, atrid, aprid = get_packet_keys(task_status)
        key = (atrid, aprid)
        apacket = self.actionable_packets.get(key, None)
        if apacket is not None:
            apacket.add_or_update_task(task_status)
            self._update_snapshot(apacket)
            return
        tslist = self.tasks.get(jid, None)
        if tslist is not None:
            tslist.put(task_status)
        else:
            tslist = TaskStatusList(task_status)
            self.tasks[jid] = tslist

    def purge_transaction(self, amie_transaction_id):
        """Delete all ActionablePacket data for the indicated transaction

        :param amie_transaction_id: The AMIE transaction identifier
        :type amie_transaction_id: str
        """
        keys = []
        for key, apacket in self.actionable_packets.items():
            atrid, aprid = key
            if atrid == amie_transaction_id:
                keys.append(key)
        for key in keys:
            apacket = self.actionable_packets[key]
            del self.actionable_packets[key]
            self._delete_snapshot(apacket)

    def service_actionable_packets(self) -> list:
        """Pass all ActionablePacket objects to the appropriate packet handler

        A packet handler will only work on a packet's tasks until it needs to
        wait for something, or until all tasks are completely done (successful
        or not). If all tasks are done, a reply packet will be sent to AMIE.
        In normal operation, this is called in a loop.

        :return: List of AMIE packets to send back to AMIE
        """
        reply_packets = list()
        actionable_packets = list(self.actionable_packets.values())
        actionable_packets.sort(key=lambda ap: ap['amie_packet_timestamp'])
        amie_packet_expected = False
        for apacket in actionable_packets:
            reply_packet = self._service_actionable_packet(apacket)
            if reply_packet:
                reply_packets.append(reply_packet)
                self.logger.debug("ServiceManager processed apacket "+\
                              "(job_id=" + apacket['job_id'] +\
                                  "), got reply AMIEPacket from handler, type="+reply_packet.packet_type)
        return reply_packets

    def get_expected_task_update_flags(self):
        # return (timely_updates_expected, updates_expected)
        task_updates_expected = False
        for tasklist in self.tasks.values():
            for task in tasklist.get_list():
                state = task['task_state']
                if state == 'in-progress' or \
                   state == 'delegated' or \
                   state == 'syncing':
                    return (True, True)
                elif state == 'nascent' or \
                     state == 'queued':
                    task_updates_expected = True
        return (False, task_updates_expected)

    def _purge_obsolete_task_transactions(self) -> set:
        if not self.actionable_packets:
            # in case we haven't yet updated the set of actionable packets
            return

        target_atrids = set()
        for tslist in self.tasks.values():
            for ts in tslist.get_name_map().values():
                target_atrids.add(ts['amie_transaction_id'])

        for apacket in self.actionable_packets.values():
            target_atrids.discard(apacket['amie_transaction_id'])

        for atrid in target_atrids:
            self.purge_transaction(atrid)


    def _service_actionable_packet(self, apacket):
        try:
            self.logger.debug("Processing apacket: "+apacket.mk_name()+" ts="+str(apacket['timestamp']))
            reply_packet = self._handle_packet(apacket)

        except ServiceProviderTimeout as spto:
            ts = apacket.find_active_task()
            if ts is not None:
                return None
            msg = self._build_log_message(apacket,spto)
            self.logger.info(msg)
            raise spto
        except ServiceProviderRequestFailed as sprf:
            return apacket['amie_packet'].reply_with_failure(message=str(sprf))
        except Exception as err:
            msg = self._build_log_message(apacket,err)
            self.logger.info(msg)
            raise err

        return reply_packet

    def _handle_packet(self, apacket):
        # Return reply Packet, or None if the apacket still has an active task
        handler = PacketHandler.get_handler(apacket['packet_type'])
        before_timestamp = apacket['timestamp']
        ts_or_reply_packet = handler.work(apacket)
        after_timestamp = apacket['timestamp']
        if isinstance(ts_or_reply_packet,TaskStatus):
            if after_timestamp > before_timestamp:
                self._update_snapshot(apacket)
            ts = ts_or_reply_packet
            task_state = ts['task_state']
            if task_state == 'successful':
                msg = "work() returned successful state in TaskStatus"
                raise PacketHandlerError(msg)
            elif task_state == 'errored':
                msg = 'task errored at ' + ts.timestamp + ": " + \
                    ts['message']
                raise PacketHandlerError(msg)
            elif task_state == 'failed':
                packet = apacket['amie_packet']
                return packet.reply_with_failure(message=ts['message'])
            else:
                self.logdumper.debug("handler returned unfinished task: ",ts)
            return None
        elif isinstance(ts_or_reply_packet,AMIEPacket):
            self._write_final_snapshot(apacket)
            apstr = to_expanded_string(apacket)
            return ts_or_reply_packet
        else:
            msg = "work() returned bad object: " + str(ts_or_reply_packet)
            raise PacketHandlerError(msg)


    def _add_apacket_to_snapshots(self, apacket):
        key = apacket.mk_name()
        initial_snap_data = dict(apacket)
        for ek in SNAPSHOT_EXCLUDE_KEYS:
            initial_snap_data.pop(ek)
        self.initial_snapshot_data[key] = initial_snap_data
        apdict = self._build_snapshot_dict(apacket)
        self.snapshots.update(key, apdict)

    def _update_snapshot(self, apacket):
        key = apacket.mk_name()
        initial_data = self.initial_snapshot_data.get(key, {})
        apdict = self._build_snapshot_dict(apacket, initial_data)
        self.snapshots.update(key,apdict)

    def _write_final_snapshot(self, apacket):
        key = apacket.mk_name()
        apdict = self._build_snapshot_dict(apacket)
        self.snapshots.update(key,apdict)

    def _build_snapshot_dict(self, apacket, exclude_dict=None):
        apdict = dict()
        curr_keys = set(apacket.keys())
        for key in SNAPSHOT_EXCLUDE_KEYS:
            curr_keys.discard(key)
        for key in SNAPSHOT_DFLT_KEYS:
            data = apacket.get(key,None)
            if key == 'tasks':
                fdata = self._build_task_snapshot_list(data)
            else:
                fdata = to_expanded_string(data)
            apdict[key] = fdata
            curr_keys.discard(key)
        if exclude_dict is None:
            return apdict
        for key in curr_keys:
            initial_val = exclude_dict.get(key, None)
            ap_val = apacket.get(key,None)
            if ap_val != initial_val:
                apdict[key] = to_expanded_string(ap_val)
        return apdict

    def _build_task_snapshot_list(self, task_status_list):
        snaptasks = list()
        if task_status_list is None:
            return snaptasks
        aptasks = task_status_list.get_list()
        for aptask in aptasks:
            snaptask = dict()
            for task_key in SNAPSHOT_DFLT_TASK_KEYS:
                snaptask[task_key] = aptask[task_key]
            snaptasks.append(snaptask)
        return snaptasks
                
    def _delete_snapshot(self, apacket):
        key = apacket.mk_name()
        self.initial_snapshot_data.pop(key,None)
        self.snapshot_data.pop(key,None)
        self.snapshots.delete(key)

    def _build_log_message(self, apacket, err):
        m = "error while processing " + \
            f"{apacket['packet_type']}." + \
            f"{apacket['amie_transaction_id']}#" + \
            f"{apacket['amie_packet_rec_id']}: " + str(err)

