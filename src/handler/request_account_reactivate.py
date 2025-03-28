from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import (truthy, get_first_nonEmpty)
import handler.subtasks as sub

class RequestAccountReactivate(PacketHandler, packet_type="request_account_reactivate"):

    def work(self, apacket):
        """Handle a "request_account_reactivate" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """
        
        spa = self.sp_adapter

        person_id = apacket.get('person_id',None)
        if person_id is None:
            person_id = apacket.get('PersonID',None)
            apacket['person_id'] = person_id
            
        person_active = apacket.get('person_active',False)
        if not person_active:
            ts = sub.activate_person(spa, apacket, 'User')
            if ts:
                return ts
        person_active = apacket['person_active']

        person_id = get_first_nonEmpty(apacket,'person_id','PersonID')
        apacket['PersonID'] = person_id
        project_id = get_first_nonEmpty('project_id','ProjectID')
        apacket['ProjectID'] = project_id
        user_notified = apacket.get('user_notified', None)
        if user_notified is None:
            ts = sub.notify_user(spa, apacket)
            if ts:
                return ts
        
        reactivate_ts = spa.reactivate_account(apacket)
        if reactivate_ts['task_state'] == "successful":
            nar = apacket.create_reply_packet()
            nar.PersonID = apacket['PersonID']
            nar.ProjectID = apacket['ProjectID']
            nar.ResourceList = apacket['ResourceList']
            return nar
        return reactivate_ts
