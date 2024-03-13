#!/usr/bin/env python
import unittest
from misctypes import DateTime
from amieparms import (transform_value,AMIEParmDescAware)
from person import (AMIEPerson, LookupPerson, ChooseOrAddPerson)

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

class TestAMIEPerson(unittest.TestCase):
    def test_constructor(self):
        parm2type = AMIEPerson.parm2type
        func_info = AMIEPerson.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        inparms['Nosuch'] = 'Nosuch_val'

        in2 = inparms.copy()
        del in2['PersonID']
        with self.assertRaises(KeyError,
                               msg="PersonID not required"):
            p = AMIEPerson(**in2)

        in2 = inparms.copy()
        del in2['FirstName']
        del in2['LastName']
        with self.assertRaises(KeyError,
                               msg="FirstName or LastName not required"):
            p = AMIEPerson(**in2)

        p = AMIEPerson(**inparms)

        self.assertTrue(isinstance(p,AMIEPerson), msg='constructor failed');
        self.assertFalse('Nosuch' in p, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = p[key]
            self.assertEqual(val,expected_val)
            

class TestLookupPerson(unittest.TestCase):
    def test_constructor(self):
        parm2type = LookupPerson.parm2type
        func_info = LookupPerson.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        inparms['Nosuch'] = 'Nosuch_val'

        in2 = inparms.copy()
        del in2['PersonID']
        p = LookupPerson(**in2)
        self.assertTrue(isinstance(p,LookupPerson),
                        msg='constructor failed');

        in2 = inparms.copy()
        del in2['GlobalID']
        p = LookupPerson(**in2)
        self.assertTrue(isinstance(p,LookupPerson),
                        msg='constructor failed');

        in2 = inparms.copy()
        del in2['PersonID']
        del in2['GlobalID']
        with self.assertRaises(KeyError,
                               msg="PersonID or GlobalID not required"):
            p = LookupPerson(**in2)

        p = LookupPerson(**inparms)

        self.assertTrue(isinstance(p,LookupPerson), msg='constructor failed');
        self.assertFalse('Nosuch' in p, msg='invalid key accepted')

class TestChooseOrAddPerson(unittest.TestCase):
    def test_constructor(self):
        parm2type = ChooseOrAddPerson.parm2type
        func_info = ChooseOrAddPerson.__init__.func_info
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
            p = ChooseOrAddPerson(**in2)

        in2 = inparms.copy()
        del in2['task_name']
        with self.assertRaises(KeyError,
                               msg="task_name not required"):
            p = ChooseOrAddPerson(**in2)

        in2 = inparms.copy()
        del in2['FirstName']
        del in2['LastName']
        with self.assertRaises(KeyError,
                               msg="FirstName or LastName not required"):
            p = ChooseOrAddPerson(**in2)

        in2 = inparms.copy()
        del in2['Email']
        with self.assertRaises(KeyError,
                               msg="Email not required"):
            p = ChooseOrAddPerson(**in2)

        in2 = inparms.copy()
        del in2['Organization']
        with self.assertRaises(KeyError,
                               msg="Organization not required"):
            p = ChooseOrAddPerson(**in2)

        p = ChooseOrAddPerson(**inparms)

        self.assertTrue(isinstance(p,ChooseOrAddPerson), msg='constructor failed');
        self.assertFalse('Nosuch' in p, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = p[key]
            self.assertEqual(val,expected_val)
            

        
if __name__ == '__main__':
    unittest.main()
