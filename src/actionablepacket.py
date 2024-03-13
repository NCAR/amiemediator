from amieclient.packet.base import Packet as AMIEPacket
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from misctypes import DateTime
from amieparms import get_packet_keys
from taskstatus import (State, TaskStatus, TaskStatusList)

class ActionablePacket(Prettifiable,dict):

    def __init__(self, amie_packet, tasks=None):
        """Create a packet dict usable by ServiceProviders from an AMIE packet

        The dict will contain the following entries::
        
            job_id                 : string that uniquely identifies a related
                                     set of tasks
            packet_type            : AMIE packet type
            amie_packet_timestamp  : packet update timestamp
            amie_transaction_id    : string that uniquely identifies the AMIE
                                     transaction
            amie_packet_rec_id     : string that uniquely identifies the packet
                                     within the AMIE transaction
            amie_packet            : AMIE Packet
            tasks                  : TaskStatusList for local tasks
            <amie_parms>           : entries from the Packet body

        :param amie_packet: An AMIE Packet
        :type amie_packet: amieclient.packet.base.Packet
        :param tasks: task data for the packet
        :type tasks: TaskStatusList, optional
        """
        
        job_id, atrid, aprid = get_packet_keys(amie_packet)
        apdict = self._amiepacket_to_dict(amie_packet)

        packet_type = amie_packet.packet_type
        dt = DateTime(amie_packet.packet_timestamp)
        timestamp = dt.datetime().timestamp()
        if tasks is None:
            tasks = TaskStatusList()

        apdict['job_id'] = job_id
        apdict['packet_type'] = packet_type
        apdict['amie_packet_timestamp'] = timestamp
        apdict['amie_transaction_id'] = atrid
        apdict['amie_packet_rec_id'] = aprid
        apdict['amie_packet'] = amie_packet
        apdict['timestamp'] = timestamp
        apdict['tasks'] = tasks

        dict.__init__(self,apdict)

    def _amiepacket_to_dict(self, amie_packet):
        packet_dict = amie_packet.as_dict()['body']
        
        # For some stange reason, "ResourceList" never has more than one
        # resource, so we will make it a scalar to make things easier for
        # the service provider.
        if 'ResourceList' in packet_dict:
            resources = packet_dict['ResourceList']
            packet_dict['Resource'] = resources[0] if resources else None

        return packet_dict

    def mk_name(self):
        """Return a convenient name for the ActionablePacket

        This is a normal method, but since ActionablePacket subclasses dict,
        it can be used as a static method on any dict with with the expected
        attributes ('amie_transaction_id', 'amie_packet_rec_id', and
        'packet_type'):

        name = ActionablePacket.mk_name(my_compatible_dict)

        """
        atrid = self['amie_transaction_id']
        aprid = self['amie_packet_rec_id']
        ptype = self['packet_type']
        return '{}.{}.{}'.format(atrid,aprid,ptype)

    def update(self, packet, task_status_list):
        """Update a ActionablePacket from AMIE packet and task list

        :param packet: AMIE packet
        :type packet: amieclient.packet.base.Packet
        :type task_status_list: TaskStatusList
        :param task_status_list: The list
        :type task_status_list: TaskStatusList
        """
        if task_status_list is None:
            return
        dt = DateTime(packet.packet_timestamp)
        timestamp = dt.datetime().timestamp()
        for ts in task_status_list:
            self['tasks'].put(ts)
            if ts['timestamp'] > timestamp:
                timestamp = ts['timestamp']
        if timestamp > self['timestamp']:
            self['timestamp'] = timestamp

    def add_or_update_task(self, task_status):
        """Add/update a task

        :param task_status: The task
        :type task_status: TaskStatus
        """
        
        self['tasks'].put(task_status)
        if task_status['timestamp'] > self['timestamp']:
            self['timestamp'] = task_status['timestamp']

    def find_active_task(self):
        return self['tasks'].find_active_task()

    def create_reply_packet(self):
        reply_packet = self['amie_packet'].reply_packet()
        packet_type = reply_packet.packet_type
        if packet_type == 'inform_transaction_complete':
            reply_packet.DetailCode = 1
            reply_packet.Message = "Success"
            reply_packet.StatusCode = "Success"
        return reply_packet


    EXCLUDE_PFORMAT_KEYS = {
        'amie_transaction_id',
        'amie_packet_rec_id',
        'packet_type',
        'job_id'
    }
    def pformat(self):
        # exclude amie_transaction_id, amie_packet_rec_id, packet_type, and
        # job_id, which are redundant because of mk_name()
        #
        outdict = dict()
        for key in self.keys():
            if key not in ActionablePacket.EXCLUDE_PFORMAT_KEYS:
                outdict[key] = self[key]
        return "ActionablePacket(" + self.mk_name() + "):\n" + \
            pformat(outdict)

