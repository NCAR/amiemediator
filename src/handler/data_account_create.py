from packethandler import PacketHandler

class DataAccountCreate(PacketHandler, packet_type="data_account_create"):

    def work(self, apacket):
        """Handle a "data_account_create" packet

        :param apacket: dict with extended packet data
        :type apacket: ActionablePacket
        :return: A TaskStatus if there is an uncompleted task, or an AMIEPacket
            to be sent back
        """

        spa = self.sp_adapter

        spa.clear_transaction(apacket)

        itc = apacket.create_reply_packet()
        return itc
