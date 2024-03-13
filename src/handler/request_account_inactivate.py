from packethandler import PacketHandler
from misctypes import DateTime
from taskstatus import TaskStatus
from miscfuncs import truthy

class RequestAccountInactivate(PacketHandler, packet_type="request_account_inactivate"):

    def work(self, apacket):
        """Handle a "request_account_inactivate" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """
        
        spa = self.sp_adapter

        inactivate_ts = spa.inactivate_account(apacket)
        if inactivate_ts['task_state'] == "successful":
            nai = apacket.create_reply_packet()
            nai.PersonID = apacket['PersonID']
            nai.ProjectID = apacket['ProjectID']
            nai.ResourceList = apacket['ResourceList']
            return nai
        return inactivate_ts
