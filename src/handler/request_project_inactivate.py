from packethandler import PacketHandler
from taskstatus import TaskStatus

class RequestProjectInactivate(PacketHandler,
                               packet_type="request_project_inactivate"):

    def work(self, apacket):
        """Handle a "request_project_inactivate" packet

        Inactivate the project and all accounts on the project

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """

        spa = self.sp_adapter
        inact_project_ts = spa.inactivate_project(apacket)
        if inact_project_ts['task_state'] == "successful":
            project_id = inact_project_ts.get_product_value('ProjectID')
        else:
            return inact_project_ts

        npi = apacket.create_reply_packet()
        npi.ProjectID = apacket['ProjectID']
        npi.ResourceList = apacket['ResourceList']
        return npi
