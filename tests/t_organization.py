#!/usr/bin/env python
import unittest
from misctypes import DateTime
from amieparms import (transform_value,AMIEParmDescAware)
from organization import (AMIEOrg, LookupOrg, ChooseOrAddOrg)

def _make_test_value(parm2type,key):
    t = parm2type[key]
    if isinstance(t,list):
        val = []
    elif t is list:
        val = []
    elif t is dict:
        val = {}
    elif t is DateTime:
        val = DateTime.now()
    elif t is not str:
        val = t(1)
    else:
        val = key + "_val"
    return val

class TestAMIEOrg(unittest.TestCase):
    def test_constructor(self):
        parm2type = AMIEOrg.parm2type
        func_info = AMIEOrg.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        inparms['Nosuch'] = 'Nosuch_val'

        in2 = inparms.copy()
        del in2['OrgCode']
        with self.assertRaises(KeyError,
                               msg="OrgCode not required"):
            o = AMIEOrg(**in2)

        in2 = inparms.copy()
        del in2['Organization']
        with self.assertRaises(KeyError,
                               msg="Organization not required"):
            o = AMIEOrg(**in2)

        o = AMIEOrg(**inparms)

        self.assertTrue(isinstance(o,AMIEOrg), msg='constructor failed');
        self.assertFalse('Nosuch' in o, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = o[key]
            self.assertEqual(val,expected_val)
            

class TestLookupOrg(unittest.TestCase):
    def test_constructor(self):
        parm2type = LookupOrg.parm2type
        func_info = LookupOrg.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        inparms['Nosuch'] = 'Nosuch_val'

        in2 = inparms.copy()
        del in2['OrgCode']
        with self.assertRaises(KeyError,
                               msg="OrgCode not required"):
            o = LookupOrg(**in2)

        o = LookupOrg(**inparms)

        self.assertTrue(isinstance(o,LookupOrg), msg='constructor failed');
        self.assertFalse('Nosuch' in o, msg='invalid key accepted')

class TestChooseOrAddOrg(unittest.TestCase):
    def test_constructor(self):
        parm2type = ChooseOrAddOrg.parm2type
        func_info = ChooseOrAddOrg.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        inparms['Nosuch'] = 'Nosuch_val'

        in2 = inparms.copy()
        del in2['job_id']
        with self.assertRaises(KeyError,
                               msg="job_id not required"):
            o = ChooseOrAddOrg(**in2)

        in2 = inparms.copy()
        del in2['task_name']
        with self.assertRaises(KeyError,
                               msg="task_name not required"):
            o = ChooseOrAddOrg(**in2)

        in2 = inparms.copy()
        del in2['OrgCode']
        del in2['Organization']
        with self.assertRaises(KeyError,
                               msg="OrgCode or Organization not required"):
            o = ChooseOrAddOrg(**in2)

        o = ChooseOrAddOrg(**inparms)

        self.assertTrue(isinstance(o,ChooseOrAddOrg), msg='constructor failed');
        self.assertFalse('Nosuch' in o, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = o[key]
            self.assertEqual(val,expected_val)
            

        
if __name__ == '__main__':
    unittest.main()
