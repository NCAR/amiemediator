#!/usr/bin/env python
import unittest
import json
import copy
from datetime import datetime
from misctypes import DateTime
from amieparms import transform_value
from taskstatus import (State, Product, TaskStatus, TaskStatusList)

class TestState(unittest.TestCase):
    def test_constructor(self):
        with self.assertRaises(TypeError,
                               msg="illegal value accepted"):
            s = State('foo')

        s = State('queued')
        self.assertTrue(isinstance(s,State),
                        msg="constructor failed")
        self.assertTrue(isinstance(s,str),
                        msg="State is not a str")
        self.assertEqual(s,"queued",
                        msg="State value is wrong")
        
class TestProduct(unittest.TestCase):
    def test_constructor(self):
        with self.assertRaises(KeyError,
                               msg="Required parm name is missing"):
            p = Product({})

        p = Product(name='myname')

        self.assertEqual(p['name'],"myname",
                         msg="name not passed in")
        self.assertEqual(p.get('value'),None,
                         msg="value set")

        p = Product(name='myname',
                    value='myid')

        self.assertEqual(p['name'],"myname",
                         msg="name not passed in")
        self.assertEqual(p['value'],"myid",
                         msg="value not passed in")
        
class TestProductList(unittest.TestCase):
    def test_constructor(self):
        listparms = [
            {'name': 'dname1', 'value': 'did1'},
            {'name': 'dname2', 'value': 'did2'},
        ]
        
        plist = transform_value([Product],listparms)
        self.assertEqual(len(plist),2,
                         msg="list wrong length")
        i=0
        for p in plist:
            i += 1
            self.assertEqual(p['name'],"dname"+str(i),
                             msg="name in list not passed in")
            self.assertEqual(p['value'],"did"+str(i),
                             msg="value in list not passed in")


class TestTaskStatus(unittest.TestCase):
    def setUp(self):
        self.testtime_s = "2023-01-01T12:00:00-07:00"
        self.testtime = datetime.fromisoformat(self.testtime_s);
        self.dictparms = {
            'amie_packet_type': "test_type",
            'job_id': "myatid:mypid",
            'amie_transaction_id': "myatid",
            'amie_packet_id': "mypid",
            'task_name': "mytaskname",
            'task_state': "queued",
            'timestamp': self.testtime,
            'products': [
                {'name': 'dname1', 'value': 'did1'},
                {'name': 'dname2', 'value': 'did2'},
            ],
        }
        self.fail_product = Product(name='FAILED', value='fail')
        self.error_product = Product(name='ERRORED', value='error')
        encodeable_dictparms = self.dictparms.copy()
        encodeable_dictparms['timestamp'] = self.testtime_s
        self.strparms = json.dumps(encodeable_dictparms)
        
    def test_constructor(self):
        parms = copy.deepcopy(self.dictparms)
        parms.pop('products')
        for parm in parms.keys():
            tparms = parms.copy()
            tparms.pop(parm)
            with self.assertRaises(KeyError,
                                   msg="Required parm " + parm + " is missing"):
                ts = TaskStatus(**tparms)

        tparms = copy.deepcopy(parms)
        tparms['task_state'] = 'nosuchstate';
        with self.assertRaises(TypeError,
                               msg="Invalid task_state accepted"):
            ts = TaskStatus(**tparms)

        tparms['task_state'] = 'failed';
        with self.assertRaises(KeyError,
                               msg="message Product not defined when status='failed'"):
            ts = TaskStatus(**tparms)

        tparms['task_state'] = 'errored';
        with self.assertRaises(KeyError,
                               msg="message Product not defined when status='errored'"):
            ts = TaskStatus(**tparms)

        parms = copy.deepcopy(self.dictparms)
        parms.pop('products')
        ts = TaskStatus(**parms)
        self.validate_instance(ts)
        self.assertEqual(len(ts['products']),0,
                         msg="products[] not empty")
 
        parms = copy.deepcopy(self.dictparms)
        parms['timestamp'] = self.testtime_s
        ts = TaskStatus(**parms)
        self.validate_instance(ts)
        self.assertEqual(ts['timestamp'],self.testtime_s,
                         msg="testtime string not accepted")
        self.assertEqual(len(ts['products']),2,
                        msg="products[] not expected size")

        fparms = copy.deepcopy(parms)
        prods = fparms['products']
        prods.append(self.fail_product)
        ts = TaskStatus(**fparms)
        self.validate_instance(ts)
        self.assertEqual(ts['task_state'],'failed',
                         msg="fail state not set")
        emsg = ts.get_product_value("FAILED")
        self.assertEqual(emsg,'fail',
                         msg="fail message not set")

        eparms = parms.copy()
        prods = eparms['products']
        prods.append(self.error_product)
        ts = TaskStatus(**eparms)
        self.validate_instance(ts)
        self.assertEqual(ts['task_state'],'errored',
                         msg="error state not set")
        emsg = ts.get_product_value("ERRORED")
        self.assertEqual(emsg,'error',
                         msg="error message not set")
        

    def test_from_dict(self):
        ts = TaskStatus(self.dictparms)
        self.validate_instance(ts)
        self.assertEqual(len(ts['products']),2,
                         msg="products[] not expected size")

    def test_from_string(self):
        ts = TaskStatus(self.strparms)
        self.validate_instance(ts)
        self.assertEqual(len(ts['products']),2,
                         msg="products[] not expected size")

    def validate_instance(self,ts):
        self.assertTrue(isinstance(ts,TaskStatus))
        self.assertTrue(isinstance(ts,dict))
        self.assertEqual(ts['job_id'],"myatid:mypid",
                         msg="task_name not passed in")
        self.assertEqual(ts['amie_transaction_id'],"myatid",
                         msg="amie_transaction_id not passed in")
        self.assertEqual(ts['amie_packet_id'],"mypid",
                         msg="amie_packet_id not passed in")
        self.assertEqual(ts['task_name'],"mytaskname",
                         msg="task_name not passed in")
        self.assertEqual(ts['timestamp'],self.testtime_s,
                         msg="testtime not passed in")
        self.assertTrue(isinstance(ts['products'],list),
                        msg="products[] not created")
        expected_state = "queued"
        for p in ts['products']:
            self.assertTrue(isinstance(p,dict),
                            msg="product list has dicts")
            if p['name'] == 'FAILED':
                expected_state = "failed"
            elif p['name'] == 'ERRORED':
                expected_state = "errored"
        self.assertEqual(ts['task_state'],expected_state,
                         msg="task_state not passed in")

class TestTaskStatusList(unittest.TestCase):
    def setUp(self):
        self.ts_data = [
            {
                'amie_packet_type': 'test_type',
                'job_id': '123456:TGCDE:TGCDE:NCAR:4567890',
                'amie_transaction_id': '123456:TGCDE:TGCDE:NCAR',
                'amie_packet_id': '4567890',
                'task_name': 'my_task1',
                'task_state': 'successful',
                'timestamp': DateTime("2023-08-02T15:20:00-06:00"),
            },
            {
                'amie_packet_type': 'test_type',
                'job_id': '123456:TGCDE:TGCDE:NCAR:4567892',
                'amie_transaction_id': '123456:TGCDE:TGCDE:NCAR',
                'amie_packet_id': '4567892',
                'task_name': 'my_task3',
                'task_state': 'in-progress',
                'timestamp': DateTime("2023-08-02T15:20:02-06:00"),
            },
            {
                'amie_packet_type': 'test_type',
                'job_id': '123456:TGCDE:TGCDE:NCAR:4567891',
                'amie_transaction_id': '123456:TGCDE:TGCDE:NCAR',
                'amie_packet_id': '4567891',
                'task_name': 'my_task2',
                'task_state': 'successful',
                'timestamp': DateTime("2023-08-02T15:20:01-06:00"),
            },
        ]
        self.tasks = []
        for tsd in self.ts_data:
            ts = TaskStatus(**tsd)
            self.tasks.append(ts)

    def test_constructor(self):
        tsl = TaskStatusList(self.ts_data)
        self.assertTrue(isinstance(tsl,TaskStatusList),
                        msg="constructor failed with list of dicts")
        ts_list = tsl.get_list()
        self.assertTrue(isinstance(ts_list,list),
                        msg="constructor list not set with list of dicts")
        self.assertEqual(len(ts_list),3,
                        msg="list of dicts yields bad list len")
        ts_map = tsl.get_name_map()
        self.assertTrue(isinstance(ts_map,dict),
                        msg="constructor dict not set with list of dicts")
        self.assertEqual(len(ts_map),3,
                        msg="list of dicts yields bad map len")
        iter_list = []
        for ts in tsl:
            iter_list.append(ts)
        self.assertEqual(ts_list,iter_list,
                         msg="iterator returned bad list with list of dicts")

        tsl = TaskStatusList(self.tasks)
        self.assertTrue(isinstance(tsl,TaskStatusList),
                        msg="constructor failed with list of TaskStatus")
        ts_list = tsl.get_list()
        self.assertTrue(isinstance(ts_list,list),
                        msg="constructor list not set with list of TaskStatus")
        self.assertEqual(len(ts_list),3,
                        msg="list of TaskStatus yields bad list len")
        ts_map = tsl.get_name_map()
        self.assertTrue(isinstance(ts_map,dict),
                        msg="constructor dict not set with list of TaskStatus")
        self.assertEqual(len(ts_map),3,
                        msg="list of TaskStatus yields bad map len")
        iter_list = []
        for ts in tsl:
            iter_list.append(ts)
        self.assertEqual(ts_list,iter_list,
                         msg="iterator returned bad list with list of TaskStatus")

    def test_get(self):
        tsl = TaskStatusList(self.ts_data)
        ts = tsl.get('my_task3')
        self.assertEqual(ts,tsl.get_list()[2],
                         msg="get() with known name returned wrong object")
        ts = tsl.get('my_task4')
        self.assertEqual(ts,None,
                         msg="get() with bad name did not return None")

    def test_find_active_task(self):
        tsl = TaskStatusList(self.ts_data)
        ts = tsl.find_active_task()
        self.assertEqual(ts,tsl.get_list()[2],
                         msg="find_active_task returned wrong object")

    def test_put(self):
        tsl = TaskStatusList(self.ts_data)
        ts = tsl.get('my_task3')
        newtimestamp = DateTime("2023-08-02T15:20:03-06:00")
        ts['timestamp'] = newtimestamp
        ts.error('error')
        tsl.put(ts)
        ts = tsl.get('my_task3')
        self.assertEqual(ts['timestamp'],newtimestamp,
                         msg='timestamp not updated after put()')
        self.assertEqual(ts['task_state'],'errored',
                         msg='task_state not updated after put()')
        ts = tsl.find_active_task()
        self.assertEqual(ts,None,
                         msg="find_active_task returned object")

        ts = tsl.get('my_task2')
        task2_timestamp = ts['timestamp']
        ts_dict = self.ts_data[2].copy()
        ts = TaskStatus(**ts_dict)
        ts.fail("fail")
        tsl.put(ts)
        ts_list = []
        for t in tsl:
            ts_list.append(t)
        ts = tsl.get('my_task2')
        self.assertEqual(ts,ts_list[1],
                         msg='task changed position without new timestamp')
        self.assertEqual(ts['timestamp'],task2_timestamp,
                         msg='timestamp changed inappropropriately')
        self.assertEqual(ts['task_state'],'failed',
                         msg='task_state not updated after put()')

    def test_get_amie_transaction_ids(self):
        tsl = TaskStatusList(self.ts_data)
        atrid = tsl.get_amie_transaction_id()
        self.assertEqual(atrid,"123456:TGCDE:TGCDE:NCAR")
                                   
    
if __name__ == '__main__':
    unittest.main()
