#!/usr/bin/env python
import unittest

from amieclient.packet.base import Packet
from amieclient.packet.project import RequestProjectCreate
from fixtures.request_project_create import RPC_PKT_1
from fixtures.request_account_create import RAC_PKT_1
from amieparms import get_packet_keys
from organization import AMIEOrg
from person import AMIEPerson
from taskstatus import (TaskStatus, TaskStatusList)
from serviceprovider import (ServiceProvider, SPSession)
from packetmanager import ActionablePacket
from packethandler import ServiceProviderAdapter

class MockActionablePacket():
    def __init__(self, task_status_list):
        self.counter = 3
        
    def work(self):
        self.counter -= 1
        return (self.counter > 0)
    
class TestServiceProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.rpc_packet1 = Packet.from_dict(RPC_PKT_1)
        self.rac_packet1 = Packet.from_dict(RAC_PKT_1)

        sp = ServiceProvider()
        sp_config = {
            'package': '',
            'module': 'serviceproviderspy',
            }
        sp.apply_config(sp_config)
        self.spspy = sp.implem

        SPSession.configure(sp=sp,
                            min_retry_delay=1, max_retry_delay=30,
                            retry_time_max=90)
        
    def test_lookup_person(self):
        apacket = ActionablePacket(self.rpc_packet1)
        spa = ServiceProviderAdapter()
        person = spa.lookup_person(apacket,"Pi")

        args = self.spspy.args['lookup_person']

        self.assertTrue(isinstance(person,AMIEPerson),
                        msg="AMIEOrg not returned")
        self.assertEqual(person['PersonID'], "12345",
                         msg="PersonID not set")
        self.assertEqual(args['GlobalID'],'71691',
                         msg='GlobalID arg not passed')
        self.assertFalse('Abstract' in args,
                         msg='non-person arg passed')
        
    def test_lookup_org(self):
        apacket = ActionablePacket(self.rpc_packet1)
        spa = ServiceProviderAdapter()
        org = spa.lookup_org(apacket,"Pi")

        args = self.spspy.args['lookup_org']

        self.assertTrue(isinstance(org,AMIEOrg),
                        msg="AMIEOrg not returned")
        self.assertEqual(org['OrgCode'], "0032425",
                         msg="OrgCode not set")
        self.assertEqual(args['OrgCode'],'0032425',
                         msg='OrgCode arg not passed')
        self.assertFalse('Abstract' in args,
                         msg='non-org arg passed')
        
    def test_choose_or_add_org(self):
        apacket = ActionablePacket(self.rpc_packet1)

        jid, atrid, pid = get_packet_keys(apacket)
        spa = ServiceProviderAdapter()
        for i in range(2):
            ts = spa.choose_or_add_org(apacket,"Pi")

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'choose_or_add_org',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['choose_or_add_org']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'choose_or_add_org',
                             msg='args task_name not set')
            self.assertEqual(args['OrgCode'],apacket['PiOrgCode'],
                             msg='args OrgCode not set')
        
    def test_choose_or_add_person(self):
        apacket = ActionablePacket(self.rpc_packet1)

        jid, atrid, pid = get_packet_keys(apacket)
        spa = ServiceProviderAdapter()
        for i in range(2):
            ts = spa.choose_or_add_person(apacket,"Pi")

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'choose_or_add_person',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['choose_or_add_person']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'choose_or_add_person',
                             msg='args task_name not set')
            self.assertEqual(args['FirstName'],apacket['PiFirstName'],
                             msg='args FirstName not set')
        
    def test_lookup_grant(self):
        apacket = ActionablePacket(self.rpc_packet1)
        spa = ServiceProviderAdapter()
        site_grant_key = spa.lookup_grant(apacket)

        args = self.spspy.args['lookup_grant']

        self.assertTrue(isinstance(site_grant_key,str),
                        msg="str not returned")
        self.assertEqual(site_grant_key, "IRI120015",
                         msg="site_grant_key not returned")
        
    def test_choose_or_add_grant(self):
        apacket = ActionablePacket(self.rpc_packet1)
        apacket['PiPersonID'] = "vraunak"

        jid, atrid, pid = get_packet_keys(apacket)
        spa = ServiceProviderAdapter()
        for i in range(2):
            ts = spa.choose_or_add_grant(apacket)

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],
                             'choose_or_add_grant',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['choose_or_add_grant']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],
                             'choose_or_add_grant',
                             msg='args task_name not set')
            self.assertEqual(args['GrantNumber'],apacket['GrantNumber'],
                             msg='args GrantNumber not set')

    def test_create_project(self):
        apacket = ActionablePacket(self.rpc_packet1)
        apacket['site_grant_key'] = "IRI120015"
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.create_project(apacket,'112157')

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'create_project',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['create_project']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'create_project',
                             msg='args task_name not set')
            self.assertEqual(args['PiPersonID'],'112157',
                             msg='args PiPersonID not set')
        
    def test_inactivate_project(self):
        apacket = ActionablePacket(self.rpc_packet1)
        apacket['ProjectID'] = "CMU139"
        apacket['site_grant_key'] = "IRI120015"
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.inactivate_project(apacket)

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'inactivate_project',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['inactivate_project']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'inactivate_project',
                             msg='args task_name not set')
            self.assertEqual(args['ProjectID'],'CMU139',
                             msg='args ProjectID not set')
        
    def test_reactivate_project(self):
        apacket = ActionablePacket(self.rpc_packet1)
        apacket['ProjectID'] = "CMU139"
        apacket['site_grant_key'] = "IRI120015"
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.reactivate_project(apacket)

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'reactivate_project',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['reactivate_project']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],prid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'reactivate_project',
                             msg='args task_name not set')
            self.assertEqual(args['ProjectID'],'CMU139',
                             msg='args ProjectID not set')
        
    def test_create_account(self):
        apacket = ActionablePacket(self.rac_packet1)
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.create_account(apacket,'112157')

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],
                             'create_account.ProjectID:PersonID',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['create_account']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],
                             'create_account.ProjectID:PersonID',
                             msg='args task_name not set')
            self.assertEqual(args['PersonID'],'112157',
                             msg='args PersonID not set')
        
    def test_inactivate_account(self):
        apacket = ActionablePacket(self.rac_packet1)
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.inactivate_account(apacket,"User")

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'inactivate_account',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['inactivate_account']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'inactivate_account',
                             msg='args task_name not set')
            self.assertEqual(args['PersonID'],'112157',
                             msg='args PersonID not set')
        
    def test_reactivate_account(self):
        apacket = ActionablePacket(self.rac_packet1)
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.reactivate_account(apacket,"User")

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'reactivate_account',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['reactivate_account']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'reactivate_account',
                             msg='args task_name not set')
            self.assertEqual(args['PersonID'],'112157',
                             msg='args PersonID not set')
        
    def test_update_allocation(self):
        apacket = ActionablePacket(self.rpc_packet1)
        apacket['ProjectID'] = "CMU139"
        spa = ServiceProviderAdapter()

        jid, atrid, pid = get_packet_keys(apacket)
        for i in range(2):
            ts = spa.update_allocation(apacket)

            self.assertEqual(ts['job_id'],jid,
                             msg='ts job_id not set')
            self.assertEqual(ts['amie_transaction_id'],atrid,
                             msg='ts amie_transaction_id not set')
            self.assertEqual(ts['amie_packet_id'],pid,
                             msg='ts amie_packet_id not set')
            self.assertEqual(ts['task_name'],'update_allocation',
                             msg='ts task_name not set')
            self.assertEqual(ts['task_state'],'queued',
                             msg='ts task_name not set')
            args = self.spspy.args['update_allocation']
            self.assertEqual(args['job_id'],jid,
                             msg='args job_id not set')
            self.assertEqual(args['amie_transaction_id'],atrid,
                             msg='args amie_transaction_id not set')
            self.assertEqual(args['amie_packet_id'],pid,
                             msg='args amie_packet_id not set')
            self.assertEqual(args['task_name'],'update_allocation',
                             msg='args task_name not set')
            self.assertEqual(args['ProjectID'],'CMU139',
                             msg='args ProjectID not set')

if __name__ == '__main__':
    unittest.main()

