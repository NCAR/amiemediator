#!/usr/bin/env python
import unittest
from fixtures.request_account_create import RAC_PKT_1
from fixtures.request_project_create import RPC_PKT_1
from amieclient.packet.base import Packet
from parmdesc import ParmDescAware
from amieparms import (get_packet_keys, strip_key_prefix,  AMIEParmDescAware)

class TestParmDesc(unittest.TestCase):
        
    def test_init(self):
        # just by loading AMIEParmDescAware, the parm2type map in
        # ParmDescAware should have been initialized with defaults

        parm2type = ParmDescAware.parm2type

        self.assertTrue(len(parm2type) > 0,
                        msg='defaults not loaded')

        self.assertTrue('Comment' in parm2type,
                         msg='AMIE default not loaded')

    def test_get_packet_keys(self):
        packet_dict = RAC_PKT_1
        packet = Packet.from_dict(packet_dict)

        tid = packet.transaction_id
        os = packet.originating_site_name
        rs = packet.remote_site_name
        ls = packet.local_site_name
        prid = packet.packet_rec_id
        expected_jid = f"T{os}:{rs}:{ls}:{tid}:{prid}"
        expected_atrid = f"{os}:{rs}:{ls}:{tid}"
        expected_aprid = str(packet.packet_rec_id)
        jid, atrid, aprid = get_packet_keys(packet)

        self.assertEqual(expected_jid,jid,
                         msg="AMIE Packet did not yield expected key")
        self.assertEqual(expected_atrid,atrid,
                         msg="AMIE Packet did not yield expected atrid")
        self.assertEqual(expected_aprid,aprid,
                         msg="AMIE Packet did not yield expected aprid")

        jid, atrid, aprid = get_packet_keys(packet_dict)
        self.assertEqual(expected_jid,jid,
                         msg="AMIE Packet dict did not yield expected key")
        self.assertEqual(expected_atrid,atrid,
                         msg="AMIE Packet did not yield expected atrid")
        self.assertEqual(expected_aprid,aprid,
                         msg="AMIE Packet did not yield expected aprid")

        packet_dict = RPC_PKT_1
        packet = Packet.from_dict(packet_dict)
        tid = packet.transaction_id
        os = packet.originating_site_name
        rs = packet.remote_site_name
        ls = packet.local_site_name
        prid = packet.packet_rec_id
        rid = packet.RecordID
        expected_jid = "R"+str(packet.RecordID)
        expected_atrid = f"{os}:{rs}:{ls}:{tid}"
        expected_aprid = str(packet.packet_rec_id)
        jid, atrid, aprid = get_packet_keys(packet)

        self.assertEqual(expected_jid,jid,
                         msg="AMIE Packet did not yield expected key")
        jid, atrid, aprid = get_packet_keys(packet_dict)
        self.assertEqual(expected_jid,jid,
                         msg="AMIE Packet dict did not yield expected key")
        self.assertEqual(expected_atrid,atrid,
                         msg="AMIE Packet did not yield expected atrid")
        self.assertEqual(expected_aprid,aprid,
                         msg="AMIE Packet did not yield expected aprid")

        nonpacket_dict = {
            'job_id': 'R12345',
            'amie_transaction_id': 'ATRID',
            'amie_packet_rec_id': 'APRID',
            }
        jid, atrid, aprid = get_packet_keys(nonpacket_dict)
        self.assertEqual(nonpacket_dict['job_id'], jid,
                         msg="non-Packet dict did not yield expected key")
        self.assertEqual(nonpacket_dict['amie_transaction_id'],atrid,
                         msg="AMIE Packet did not yield expected atrid")
        self.assertEqual(nonpacket_dict['amie_packet_rec_id'],aprid,
                         msg="AMIE Packet did not yield expected aprid")

    def test_strip_key_prefix(self):
        in_dict={
            'UserFirstName': 'John',
            'UserLastName': 'Doe',
            'Username': 'johndoe',
            'user_name': 'john_doe',
            'FavoriteColor': 'Blue',
            }
        out_dict = strip_key_prefix("User",in_dict)
        self.assertEqual(len(out_dict),5,
                         msg="wrong number of elements copied")
        self.assertEqual(out_dict['FirstName'],'John',
                         msg="FirstName not copied")
        self.assertEqual(out_dict['LastName'],'Doe',
                         msg="LastName not copied")
        self.assertEqual(out_dict['Username'],'johndoe',
                         msg="Username not copied")
        self.assertEqual(out_dict['name'],'john_doe',
                         msg="name not copied")
        self.assertEqual(out_dict['FavoriteColor'],'Blue',
                         msg="FavoriteColor not copied")
        in_dict={
            'FavouriteColour': 'Blue. No - AHHH',
            }
        out_dict = strip_key_prefix("User",in_dict)
        self.assertFalse(out_dict is in_dict,
                         msg="copy not made")
        self.assertEqual(out_dict['FavouriteColour'],'Blue. No - AHHH',
                         msg="FavouriteColour not copied")
        
if __name__ == '__main__':
    unittest.main()
