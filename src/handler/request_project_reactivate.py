from packethandler import PacketHandler
from taskstatus import TaskStatus
import handler.subtasks as sub

class RequestProjectReactivate(PacketHandler,
                               packet_type="request_project_reactivate"):

    def work(self, apacket):
        """Handle a "request_project_reactivate" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """
        
        spa = self.sp_adapter

        reactivate_ts = spa.reactivate_project(apacket)
        if reactivate_ts['task_state'] != "successful":
            return reactivate_ts

        npr = apacket.create_reply_packet()
        npr.ProjectID = apacket['ProjectID']
        npr.ResourceList = apacket['ResourceList']

        return npr
