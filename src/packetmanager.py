import logging
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from logdumper import LogDumper
from snapshot import Snapshots
from amieclient.packet.base import Packet as AMIEPacket
from taskstatus import (State, TaskStatus)
from actionablepacket import ActionablePacket
from packethandler import (PacketHandlerError, PacketHandler)
from spexception import (ServiceProviderTimeout, ServiceProviderRequestFailed)

SNAPSHOT_DFLT_KEYS = [
    'job_id',
    'amie_packet_type',
    'amie_packet_timestamp',
    'amie_transaction_id',
    'amie_packet_id',
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

    def __init__(self, snapshot_dir):
        """Coordinate the running of tasks to service ActionablePackets

        In addition to passing ActionablePacket objects to individual handlers
        to process tasks, PacketManager maintains a directory with
        ActionablePacket "snapshots" that are updated as the objects change.
        Snapshots are files containing JSON-serialized ``ActionablePacket``
        data. Snapshots are meant to facilitate external monitoring of the AMIE
        mediator state. In particular, snapshots are NOT used by the mediator
        itself to remember the state of AMIE packets or ``ServiceProvider``
        tasks; all persistent state of this kind is the responsibility of the
        AMIE server and the local ``ServiceProvider`` implementation.
        
        Snapshots initially contain only the keys in
        :data:~packetmanager.SNAPSHOT_DFLT_KEYS` and not in
        :data:~packetmanager.SNAPSHOT_EXCLUDE_KEYS`. Updated snapshots contain
        these keys plus any keys that were not in the original
        ``ActionablePacket``. When all tasks for a packet are complete and an
        AMIE reply packet can be created, the snapshot is updated to contain
        the complete ``ActionablePacket``.

        :param site_name: the local site name
        :type site_name: str
        :param transaction_manager: Repository of stored tasks and packets
        :type site_name: TransactionManager
        :param snapshot_dir: the name of the directory for apacket snapshots
        :type site_name: str
        
        """

        self.snapshots = Snapshots(snapshot_dir, 'w')
        
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

        PacketHandler.initialize_handlers()

    def purge_actionable_packets(self, apackets):
        """Delete all data related to the given ActionablePackets

        :param apackets: Actionable packets
        :type apackets: collection of ActionablePacket
        """

        for apacket in apackets:
            self._delete_snapshot(apacket)

    def service_actionable_packets(self, apackets) -> list:
        """Pass ActionablePacket objects to the appropriate packet handler

        A packet handler will only work on a packet's tasks until it needs to
        wait for something, or until all tasks are completely done (successful
        or not). If all tasks are done, a reply packet will be returned to be
        sent to AMIE. In normal operation, this is called in a loop.

        :param apackets: Actionable packets
        :type apackets: collection of ActionablePacket
        :return: List of amieclient.packet.base.Packet
        """
        
        reply_packets = list()
        actionable_packets = list(apackets)
        actionable_packets.sort(key=lambda ap: ap['timestamp'])
        amie_packet_expected = False
        for apacket in actionable_packets:
            self._update_snapshot(apacket)
            reply_packet = self._service_actionable_packet(apacket)
            if reply_packet:
                reply_packets.append(reply_packet)
                self.logger.debug("ServiceManager processed apacket "+\
                                  "(job_id=" + apacket['job_id'] +\
                                  "), got reply AMIEPacket from handler," +\
                                  "type=" + reply_packet.__class__._packet_type)
            else:
                self._update_snapshot(apacket)
        return reply_packets

    def _service_actionable_packet(self, apacket):
        try:
            self.logger.debug("Processing apacket: "+apacket.mk_name()+" ts="+\
                              str(apacket['timestamp']))
            reply_packet = self._handle_packet(apacket)

        except ServiceProviderTimeout as spto:
            ts = apacket.find_active_task()
            if ts is not None:
                return None
            msg = self._build_log_message(apacket,spto)
            self.logger.info(msg)
            raise spto
        except ServiceProviderRequestFailed as sprf:
            return apacket.create_failure_reply_packet(message=str(sprf))
        except Exception as err:
            msg = self._build_log_message(apacket,err)
            self.logger.info(msg)
            raise err

        return reply_packet

    def _handle_packet(self, apacket):
        # Return reply Packet, or None if the apacket still has an active task
        handler = PacketHandler.get_handler(apacket['amie_packet_type'])
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
                msg = ts['message']
                return apacket.create_failure_reply_packet(message=msg)
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
        return "error while processing " + apacket.mk_name() + ": " + str(err)

