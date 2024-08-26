from packethandler import PacketHandler
import handler.subtasks as sub

class DataProjectCreate(PacketHandler, packet_type="data_project_create"):

    def work(self, apacket):
        """Handle a "data_project_create" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """

        spa = self.sp_adapter
        
        ts = sub.update_person_DNs(spa, apacket, "Pi")
        if ts:
            return ts
        
        spa.clear_transaction(apacket)

        itc = apacket.create_reply_packet()
        return itc
