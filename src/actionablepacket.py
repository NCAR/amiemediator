from amieclient.packet.base import Packet as AMIEPacket
from miscfuncs import (Prettifiable, pformat, to_expanded_string)
from misctypes import DateTime
from amieparms import (get_packet_keys, parse_atrid)
from taskstatus import (State, TaskStatus, TaskStatusList)

class ActionablePacket(Prettifiable,dict):

    @staticmethod
    def create_reply(packet)-> AMIEPacket:
        """Create a reply AMIEPacket for given AMIEPacket"""

        reply_packet = packet.reply_packet()
        packet_type = reply_packet.__class__._packet_type
        if packet_type == 'inform_transaction_complete':
            reply_packet.DetailCode = 1
            reply_packet.Message = "Success"
            reply_packet.StatusCode = "Success"
        ActionablePacket._fill_in_reply(packet, reply_packet)
        return reply_packet
    
    @staticmethod
    def create_failure_reply(packet, *args, **kwargs) -> AMIEPacket:
        """Create a reply ITC failure packet for given AMIEPacket"""
        
        reply_packet = packet.reply_with_failure(*args, **kwargs)
        ActionablePacket._fill_in_reply(packet, reply_packet)
        return reply_packet

    @staticmethod
    def _fill_in_reply(packet, reply_packet):
        # The reply packets created by amieclient's Packet.reply_packet() and
        # Packet.reply_with_failure do not have the transaction_id,
        # originating_site_name, remote_site_name, local_site_name, packet_id,
        # and (sometimes) packet_rec_id fields set, because they are not needed
        # when the in_reply_to attribute is set. However, the mediator needs
        # these fields set to extract needed keys from the reply packet.
        #
        # The transaction_id, packet_id, and packet_rec_id are created by the
        # originating site. The originating site, remote site, and local site
        # are set when the transaction is created, and along with the
        # transaction_id do not change for the lifetime of the transaction. The
        # packet_id is set by the site creating the packet, and must be unique
        # for the creating site within the transaction. We just assume the AMIE
        # server is allocating its packet_ids appropriately, and add a big
        # number to it, because we know it will be unique for us.
        #
        # The packet_rec_id is globally unique for the AMIE server and is
        # unset in the reply packet.
        #
        reply_packet.transaction_id = packet.transaction_id
        reply_packet.originating_site_name = packet.originating_site_name
        reply_packet.remote_site_name = packet.remote_site_name
        reply_packet.local_site_name = packet.local_site_name
        reply_packet.packet_id = packet.packet_id + 1000

    def __init__(self, amie_packet, tasks=None):
        """Create a packet dict usable by ServiceProviders from an AMIE packet

        The dict will contain the following entries::
            job_id                 : globally-unique packet id for AMIE - the
                                     Packet.packet_rec_id (not to be confused
                                     with Packet.packet_id). Since the packet
                                     is associated with a set of tasks in the
                                     ServiceProvider, we call this job_id in
                                     that context to avoid confusion with
                                     the amie_packet_id
            amie_packet_type       : AMIE packet type
            amie_packet_timestamp  : packet update timestamp
            amie_transaction_id    : string that uniquely identifies the AMIE
                                     transaction
            amie_packet_id         : string that uniquely identifies the packet
                                     within the AMIE transaction
            amie_packet            : AMIE Packet
            tasks                  : TaskStatusList for local tasks
            <amie_parms>           : entries from the Packet body

        :param amie_packet: An AMIE Packet
        :type amie_packet: amieclient.packet.base.Packet
        :param tasks: task data for the packet
        :type tasks: TaskStatusList, optional
        """

        apdict = self._amiepacket_to_dict(amie_packet)
        job_id, atrid, pid = get_packet_keys(amie_packet)
        packet_type = amie_packet.__class__._packet_type
        dt = DateTime(amie_packet.packet_timestamp)
        timestamp = dt.datetime().timestamp()
        if tasks is None:
            tasks = TaskStatusList()
            
        apdict['amie_packet'] = amie_packet
        apdict['amie_packet_type'] = packet_type
        apdict['job_id'] = job_id
        apdict['amie_transaction_id'] = atrid
        apdict['amie_packet_id'] = pid
        apdict['amie_packet_timestamp'] = timestamp
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
        attributes ('amie_packet_type', 'amie_transaction_id', and
        'amie_packet_id'):

        name = ActionablePacket.mk_name(my_compatible_dict)

        """
        
        ptype = self['amie_packet_type']
        atrid = self['amie_transaction_id']
        pid = self['amie_packet_id']
        return '{}.{}.{}'.format(ptype,atrid,pid)

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

    def get_tasks(self) -> TaskStatusList:
        return self['tasks']

    def find_active_task(self):
        return self['tasks'].find_active_task()

    def create_reply_packet(self):
        packet = self['amie_packet']
        return ActionablePacket.create_reply(packet)

    def create_failure_reply_packet(self, *args, **kwargs):
        packet = self['amie_packet']
        return ActionablePacket.create_failure_reply(packet, *args, **kwargs)

    
    EXCLUDE_PFORMAT_KEYS = {
        'amie_transaction_id',
        'amie_packet_id',
        'amie_packet_type'
    }
    
    def pformat(self):
        # exclude amie_transaction_id, amie_packet_id, and amie_packet_type,
        # which are redundant because of mk_name()
        #
        outdict = dict()
        for key in self.keys():
            if key not in ActionablePacket.EXCLUDE_PFORMAT_KEYS:
                outdict[key] = self[key]
        return "ActionablePacket(" + self.mk_name() + "):\n" + \
            pformat(outdict)

