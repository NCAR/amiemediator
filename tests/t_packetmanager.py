#!/usr/bin/env python
import unittest
import json
from amieclient.packet.base import Packet
from amieclient.packet.project import RequestProjectCreate
from fixtures.request_project_create import (RPC_PKT_1,RPC_PKT_2)
from fixtures.inform_transaction_complete import (ITC_CANCEL_RPC_PKT_1,
                                                  ITC_CANCEL_RPC_PKT_2)
from amieparms import get_packet_keys
from taskstatus import (TaskStatus, TaskStatusList)
from test.test_sp import ServiceProvider as TestServiceProvider
from packetmanager import PacketManager

class TestPacketManager(unittest.TestCase):
    def setUp(self):
        self.packet1 = Packet.from_dict(RPC_PKT_1)
        jid, atrid, aprid = get_packet_keys(self.packet1)
        self.atrid1 = atrid
        self.aprid1 = aprid
        self.key1 = (atrid, aprid)
        self.jid1 = jid
        self.data1 = json.dumps(RPC_PKT_1['body'])
        self.packetmanager = PacketManager("SDSC")
        self.tasks_init = [
            TaskStatus(
                job_id=jid,
                amie_transaction_id=atrid,
                amie_packet_rec_id=aprid,
                task_name="task 1",
                task_state="successful",
                timestamp='2023-07-01T12:00:00-06:00',
                products=[{'prod_id':'12345','name':'PIPersonID'}]
                ),
            TaskStatus(
                job_id=jid,
                amie_transaction_id=atrid,
                amie_packet_rec_id=aprid,
                task_name="task 2",
                task_state="queued",
                timestamp='2023-07-01T12:00:01-06:00'
                )
            ]
        self.tasklist = TaskStatusList(self.tasks_init)
        self.packet2 = Packet.from_dict(RPC_PKT_2)
        jid, atrid, aprid = get_packet_keys(self.packet2)
        self.atrid2 = atrid
        self.aprid2 = aprid
        self.key2 = (atrid, aprid)
        self.jid2 = jid
        self.data2 = json.dumps(RPC_PKT_2['body'])
        self.packets = [self.packet1, self.packet2]

    def test_constructor(self):
        self.assertEqual(self.packetmanager.site_name, "SDSC",
                         msg="site_name not set")
        self.assertTrue(isinstance(self.packetmanager.tasks, dict),
                        msg="tasks map not initialized")
        self.assertEqual(len(self.packetmanager.tasks), 0,
                        msg="tasks map not empty")
        self.assertTrue(isinstance(self.packetmanager.actionable_packets, dict),
                        msg="actionable_packets map not initialized")
        self.assertEqual(len(self.packetmanager.actionable_packets), 0,
                        msg="tasks actionable_packets not empty")

            
    def test_refresh_tasks(self):
        self.packetmanager.refresh_tasks(self.tasks_init)

        self.assertEqual(len(self.packetmanager.tasks), 1,
                        msg="tasks map has wrong size")
        task_list = self.packetmanager.tasks.get(self.jid1,None)
        self.assertTrue(isinstance(task_list, TaskStatusList),
                        msg="tasks map does not contain TaskStatusList")
        tasks = task_list.get_list()
        self.assertEqual(tasks[0],self.tasks_init[0],
                         msg="task 1 not inserted correctly")
        self.assertEqual(tasks[1],self.tasks_init[1],
                         msg="task 2 not inserted correctly")

    def test_refresh_amie_packets_with_no_tasks(self):
        self.packetmanager.refresh_amie_packets(self.packets)

        apackets = self.packetmanager.get_actionable_packets()
        self.assertEqual(len(apackets), 2,
                         msg="Wrong number of new actionable packets")
        apacket1 = apackets[0]

        self.assertEqual(apacket1['job_id'], self.jid1,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket1['packet_type'], "request_project_create",
                         msg="apacket packet_type is wrong")
        self.assertEqual(apacket1['amie_transaction_id'], self.atrid1,
                         msg="apacket amie_transaction_id is wrong")
        self.assertEqual(apacket1['amie_packet_rec_id'], self.aprid1,
                         msg="apacket amie_packet_rec_id is wrong")
        self.assertEqual(len(apacket1['tasks'].get_name_map()), 0,
                         msg="apacket tasks not empty")

        apacket2 = apackets[1]

        self.assertEqual(apacket2['job_id'], self.jid2,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket2['packet_type'], "request_project_create",
                         msg="apacket packet_type is wrong")
        self.assertEqual(apacket2['amie_transaction_id'], self.atrid2,
                         msg="apacket amie_transaction_id is wrong")
        self.assertEqual(apacket2['amie_packet_rec_id'], self.aprid2,
                         msg="apacket amie_packet_rec_id is wrong")
        self.assertEqual(len(apacket2['tasks'].get_name_map()), 0,
                         msg="apacket tasks not empty")


    def test_refresh_amie_packets_with_tasks(self):
        self.packetmanager.refresh_tasks(self.tasks_init)

        self.packetmanager.refresh_amie_packets(self.packets)

        apackets = self.packetmanager.get_actionable_packets()
        self.assertEqual(len(apackets), 2,
                         msg="Wrong number of new actionable packets")
        apacket1 = apackets[0]

        self.assertEqual(apacket1['job_id'], self.jid1,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket1['packet_type'], "request_project_create",
                         msg="apacket packet_type is wrong")
        self.assertEqual(apacket1['amie_transaction_id'], self.atrid1,
                         msg="apacket amie_transaction_id is wrong")
        self.assertEqual(apacket1['amie_packet_rec_id'], self.aprid1,
                         msg="apacket amie_packet_rec_id is wrong")
        self.assertEqual(apacket1['tasks'],self.tasklist,
                         msg="apacket tasks is wrong")
                         
        apacket2 = apackets[1]

        self.assertEqual(apacket2['job_id'], self.jid2,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket2['job_id'], self.jid1,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket2['packet_type'], "request_project_create",
                         msg="apacket packet_type is wrong")
        self.assertEqual(apacket2['amie_transaction_id'], self.atrid2,
                         msg="apacket amie_transaction_id is wrong")
        self.assertNotEqual(apacket2['amie_transaction_id'], self.atrid1,
                         msg="apacket amie_transaction_id is wrong")
        self.assertEqual(apacket2['amie_packet_rec_id'], self.aprid2,
                         msg="apacket amie_packet_rec_id is wrong")
        self.assertEqual(apacket1['tasks'],self.tasklist,
                         msg="apacket tasks is wrong")

    def test_refresh_amie_packets_with_transaction_ending_itc(self):
        self.packetmanager.refresh_tasks(self.tasks_init)
        self.packetmanager.refresh_amie_packets(self.packets)

        itc = Packet.from_dict(ITC_CANCEL_RPC_PKT_2)
        self.packetmanager.refresh_amie_packets([itc])

        apackets = self.packetmanager.get_actionable_packets()
        self.assertEqual(len(apackets), 1,
                         msg="Wrong number of new actionable packets")
        
        apacket1 = apackets[0]

        self.assertEqual(apacket1['job_id'], self.jid1,
                         msg="apacket job_id is wrong")
        self.assertEqual(apacket1['packet_type'], "request_project_create",
                         msg="apacket packet_type is wrong")
        self.assertEqual(apacket1['amie_transaction_id'], self.atrid1,
                         msg="apacket amie_transaction_id is wrong")
        self.assertEqual(apacket1['amie_packet_rec_id'], self.aprid1,
                         msg="apacket amie_packet_rec_id is wrong")
        self.assertEqual(apacket1['tasks'],self.tasklist,
                         msg="apacket tasks is wrong")

    def test_find_obsolete_task_transactions(self):
        self.packetmanager.refresh_tasks(self.tasks_init)
        self.packetmanager.refresh_amie_packets([self.packet2])

        obsolete_atrids = self.packetmanager.find_obsolete_task_transactions()
        self.assertTrue(isinstance(obsolete_atrids,set),
                        msg='did not return set')
        self.assertEqual(len(obsolete_atrids),1,
                        msg='number of obsolete_task_transactions not 1')
        jid, atrid, aprid = get_packet_keys(self.packet1)
        for oatrid in obsolete_atrids:
            self.assertEqual(oatrid,atrid,
                             msg='unexpected transaction id returned')


    def test_add_or_update_task(self):
        self.packetmanager.refresh_tasks(self.tasks_init)
        self.packetmanager.refresh_amie_packets(self.packets)
        apackets = self.packetmanager.get_actionable_packets()
        apacket1 = apackets[0]

        ts_parms = self.tasks_init[1]
        ts_new_parms = ts_parms.copy()
        ts_new_parms['task_state'] = 'in-progress'
        ts_new_parms['timestamp'] = '2023-07-01T13:00:01-06:00'
        ts_new = TaskStatus(**ts_new_parms)

        self.packetmanager.add_or_update_task(ts_new)
        tslist = apacket1['tasks']
        updated_task = tslist.get('task 2')

        self.assertEqual(updated_task['task_state'], 'in-progress',
                         msg='task state not updated')
        self.assertEqual(updated_task['timestamp'], '2023-07-01T13:00:01-06:00',
                         msg='task timestamp not updated')
                        

        
if __name__ == '__main__':
    unittest.main()
