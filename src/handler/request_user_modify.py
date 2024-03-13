from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import truthy
import handler.subtasks as sub

class RequestUserModify(PacketHandler, packet_type="request_user_modify"):

    def work(self, apacket):
        """Handle a "request_user_modify" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """
        
        spa = self.sp_adapter
        
        person_id = apacket.get('PersonID',None)
        ts = sub.modify_user(spa, apacket)
        if ts:
            return ts
        
        num = apacket.create_reply_packet()
        num.ActionType = apacket['ActionType']
        num.PersonID = apacket['PersonID']
        return num
