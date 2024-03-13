#!/usr/bin/env python
import unittest
from amieclient.packet.base import Packet
from amieclient.packet.project import (RequestProjectCreate,NotifyProjectCreate)
from fixtures.request_project_create import RPC_PKT_1
from misctypes import DateTime
from taskstatus import (Product, TaskStatus)
from serviceprovider import (ServiceProvider, SPSession)
from packetmanager import ActionablePacket
from packethandler import (ServiceProviderAdapter, PacketHandler)
from handler.request_project_create import RequestProjectCreate

class TestRequestProjectCreate(unittest.TestCase):

    def setUp(self):
        self.packet_dict = RPC_PKT_1

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
        
    def test_constructor(self):
        handler = RequestProjectCreate()

        self.assertTrue(isinstance(handler,RequestProjectCreate),
                        msg="constructor failed")
        self.assertTrue(isinstance(handler.sp_adapter,ServiceProviderAdapter),
                        msg="constructor failed")


    def test_work_with_no_person(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_person_result',None)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'choose_or_add_person.PiPersonID',
                         msg='did not get expected task')
        self.assertTrue('lookup_org' not in args,
                        msg='lookup_org unexpected called')
        self.assertTrue('choose_or_add_org' not in args,
                        msg='choose_or_add_org unexpected called')
        self.assertTrue('create_project' not in args,
                        msg='create_project unexpected called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpected called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')

    def test_work_with_known_person_no_org(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_org_result',None)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpected called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'choose_or_add_org.OrgCode',
                         msg='did not get expected task')
        self.assertTrue('create_project' not in args,
                        msg='create_project unexpected called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpected called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')


    def test_work_with_created_person_no_org(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_person_result',None)
        self.spspy.set_test_data('choose_or_add_person_result',
                                 {
                                  'task_name':'choose_or_add_person.PiPersonID',
                                  'task_state':'successful',
                                  'products':[Product(name='PersonID',
                                                      value='12345')]
                                 }
                                 )
        self.spspy.set_test_data('lookup_org_result',None)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' in args,
                        msg='choose_or_add_person not called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'choose_or_add_org.OrgCode',
                         msg='did not get expected task')
        self.assertTrue('create_project' not in args,
                        msg='create_project unexpected called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpected called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')


    def test_work_with_known_person_and_org(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_grant_result',None)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpected called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'choose_or_add_grant.site_grant_key',
                         msg='did not get expected task')
        self.assertTrue('create_project' not in args,
                        msg='create_project unexpected called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpected called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')

    def test_work_with_known_person_created_org(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_org_result',None)
        self.spspy.set_test_data('choose_or_add_org_result',
                                 {
                                  'task_name':'choose_or_add_org.OrgCode',
                                  'task_state':'successful',
                                  'products':[Product(name='OrgCode',
                                                      value='0032425')]
                                 }
                                 )
        self.spspy.set_test_data('lookup_grant_result',None)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' in args,
                        msg='choose_or_add_org not called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'choose_or_add_grant.site_grant_key',
                         msg='did not get expected task')
        self.assertTrue('create_project' not in args,
                        msg='create_project unexpected called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpectedly called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpectedly called')


    def test_work_with_known_person_org_grant(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue('choose_or_add_grant' not in args,
                         msg='choose_or_add_grant unexpectedly called')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'create_project.ProjectID',
                         msg='did not get expected task')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpectedly called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')

    def test_work_with_known_person_org_created_grant(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('lookup_grant_result',None)
        self.spspy.set_test_data('choose_or_add_grant_result',
                                 {
                                  'task_name':'choose_or_add_grant.site_grant_key',
                                  'task_state':'successful',
                                  'products':[Product(name='site_grant_key',
                                                      value='IRI120015')]
                                 }
                                 )

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue('choose_or_add_grant' in args,
                        msg='choose_or_add_grant not called')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'create_project.ProjectID',
                         msg='did not get expected task')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpectedly called')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')

    def test_work_with_known_person_org_grant_created_project(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('create_project_result',
                                 {
                                  'task_name':'create_project.ProjectID',
                                  'task_state':'successful',
                                  'products':[Product(name='ProjectID',
                                                      value='CMU139')]
                                 }
                                 )

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue('choose_or_add_grant' not in args,
                        msg='choose_or_add_grant unexpectedly called')
        self.assertTrue('create_account' in args,
                        msg='create_account not called')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'create_account.ProjectID:PersonID',
                         msg='did not get expected task')
        self.assertTrue('update_allocation' not in args,
                        msg='update_allocation unexpected called')

    def test_work_with_known_person_org_grant_created_project_account_no_allocation(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('create_project_result',
                                 {
                                  'task_name':'create_project.ProjectID',
                                  'task_state':'successful',
                                  'products':[Product(name='ProjectID',
                                                      value='CMU139')]
                                 }
                                 )
        self.spspy.set_test_data('create_account_result',
                                 {
                                  'task_name':'create_project.ProjectID',
                                  'task_state':'successful',
                                  'products':[Product(name='RemoteSiteLogin',
                                                      value='vraunak')]
                                 }
                                 )

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue('choose_or_add_grant' not in args,
                        msg='choose_or_add_grant unexpectedly called')
        self.assertTrue('create_account' in args,
                        msg='create_account not called')
        self.assertTrue('update_allocation' in args,
                        msg='update_allocation not called')
        self.assertTrue(isinstance(ts_or_packet,TaskStatus),
                        msg='did not get a TaskStatus')
        self.assertEqual(ts_or_packet['task_name'],
                         'update_allocation.ServiceUnitsAllocated',
                         msg='did not get expected task')

    def test_work_with_known_person_org_grant_created_project_account_allocation(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        self.spspy.set_test_data('create_project_result',
                                 {
                                  'task_name':'create_project.ProjectID',
                                  'task_state':'successful',
                                  'products':[Product(name='ProjectID',
                                                      value='CMU139')]
                                 }
                                 )
        self.spspy.set_test_data('create_account_result',
                                 {
                                  'task_name':'create_project.ProjectID',
                                  'task_state':'successful',
                                  'products':[Product(name='RemoteSiteLogin',
                                                      value='vraunak')]
                                 }
                                 )
        self.spspy.set_test_data('update_allocation_result',
                                 {
                                  'task_name':'update_allocation.ServiceUnitsAllocated',
                                  'task_state':'successful',
                                  'products':[Product(name='ServiceUnitsAllocated',
                                                      value=10000),
                                              Product(name='StartDate',
                                                      value='2022-01-01T00:00:00Z'),
                                              Product(name='EndDate',
                                                      value='2022-07-31T23:59:59.999Z'),
                                              ]
                                 }
                                 )

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertEqual(args['lookup_person']['GlobalID'],'71691',
                         msg='lookup_person not called as expected')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertEqual(args['lookup_org']['OrgCode'],'0032425',
                         msg='lookup_org not called as expected')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertEqual(args['lookup_grant']['GrantNumber'],'IRI120015',
                         msg='lookup_grant not called as expected')
        self.assertTrue('choose_or_add_grant' not in args,
                        msg='choose_or_add_grant unexpectedly called')
        self.assertTrue('create_account' in args,
                        msg='create_account not called')
        self.assertTrue('update_allocation' in args,
                        msg='update_allocation not called')
        self.assertTrue(isinstance(ts_or_packet,NotifyProjectCreate),
                        msg='did not get a NotifyProjectCreate')
        packet = ts_or_packet
        self.assertEqual(packet.ProjectID,'CMU139',
                         msg='ProjectID not set')
        self.assertEqual(packet.PiPersonID,'12345',
                         msg='PiPersonID not set')
        self.assertEqual(packet.ServiceUnitsAllocated,10000,
                         msg='ServiceUnitsAllocated not set')
        self.assertEqual(packet.StartDate,
                         DateTime('2022-01-01T00:00:00Z').datetime(),
                         msg='StartDate not set')
        self.assertEqual(packet.EndDate,
                         DateTime('2022-07-31T23:59:59.999Z').datetime(),
                         msg='StartDate not set')

    def test_work_with_saved_values(self):
        packet_dict = self.packet_dict.copy()
        packet = Packet.from_dict(self.packet_dict)
        handler = RequestProjectCreate()
        apacket = ActionablePacket(packet)
        apacket['pi_person_id'] = '12345'
        apacket['org_code'] = '0032425'
        apacket['site_grant_key'] = 'IRI120015'
        apacket['project_id'] = 'CMU139'
        apacket['remote_site_login'] = 'vraunak'
        self.spspy.set_test_data('update_allocation_result',
                                 {
                                  'task_name':'update_allocation.ServiceUnitsAllocated',
                                  'task_state':'successful',
                                  'products':[Product(name='ServiceUnitsAllocated',
                                                      value=10000),
                                              Product(name='StartDate',
                                                      value='2022-01-01T00:00:00Z'),
                                              Product(name='EndDate',
                                                      value='2022-07-31T23:59:59.999Z'),
                                              ]
                                 }
                                 )

        ts_or_packet = handler.work(apacket)
        args = self.spspy.args

        self.assertTrue('lookup_person' not in args,
                         msg='lookup_person unexpectedly called')
        self.assertTrue('choose_or_add_person' not in args,
                        msg='choose_or_add_person unexpectedly called')
        self.assertTrue('lookup_org' not in args,
                        msg='lookup_org unexpectedly called')
        self.assertTrue('choose_or_add_org' not in args,
                         msg='choose_or_add_org unexpectedly called')
        self.assertTrue('lookup_grant' not in args,
                         msg='lookup_grant unexpectedly called')
        self.assertTrue('choose_or_add_grant' not in args,
                        msg='choose_or_add_grant unexpectedly called')
        self.assertTrue('create_project' not in args,
                         msg='create_project unexpectedly called')
        self.assertTrue('create_account' not in args,
                        msg='create_account unexpectedly called')
        self.assertTrue('update_allocation' in args,
                        msg='update_allocation not called')
        self.assertTrue(isinstance(ts_or_packet,NotifyProjectCreate),
                        msg='did not get a NotifyProjectCreate')
        packet = ts_or_packet
        self.assertEqual(packet.ProjectID,'CMU139',
                         msg='ProjectID not set')
        self.assertEqual(packet.PiPersonID,'12345',
                         msg='PiPersonID not set')
        self.assertEqual(packet.ServiceUnitsAllocated,10000,
                         msg='ServiceUnitsAllocated not set')
        self.assertEqual(packet.StartDate,
                         DateTime('2022-01-01T00:00:00Z').datetime(),
                         msg='StartDate not set')
        self.assertEqual(packet.EndDate,
                         DateTime('2022-07-31T23:59:59.999Z').datetime(),
                         msg='StartDate not set')


        
if __name__ == '__main__':
    unittest.main()
