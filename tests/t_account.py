#!/usr/bin/env python
import unittest
import json
from misctypes import DateTime
from account import (CreateAccount, InactivateAccount, ReactivateAccount)

def _make_test_value(parm2type,key):
    t = parm2type[key]
    if isinstance(t,list):
        val = []
    elif t is list:
        val = []
    elif t is dict:
        val = {}
    elif t is DateTime:
        if (key == "StartDate"):
            val = DateTime("2023-01-01T00:00:00-07:00")
        else:
            val = DateTime("2023-01-01T23:59:59-07:00")
    elif t is not str:
        val = t(1)
    else:
        val = key + "_val"
    return val

class TestCreateAccount(unittest.TestCase):
    def test_constructor(self):
        parm2type = CreateAccount.parm2type.copy()
        func_info = CreateAccount.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        parm2type['Nosuch'] = str

        reqparms = func_info['required'].copy()
        for reqparm in reqparms:
            in2 = inparms.copy()
            del in2[reqparm]
            with self.assertRaises(KeyError,
                                   msg=reqparm + " not required"):
                parms = CreateAccount(**in2)

        parms = CreateAccount(**inparms)

        self.assertTrue(isinstance(parms,CreateAccount),
                        msg='constructor() failed');
        self.assertFalse('Nosuch' in parms, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = parms[key]
            self.assertEqual(val,expected_val)

class TestInactivateAccount(unittest.TestCase):
    def test_constructor(self):
        parm2type = InactivateAccount.parm2type.copy()
        func_info = InactivateAccount.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        parm2type['Nosuch'] = str

        reqparms = func_info['required'].copy()
        for reqparm in reqparms:
            in2 = inparms.copy()
            del in2[reqparm]
            with self.assertRaises(KeyError,
                                   msg=reqparm + " not required"):
                parms = InactivateAccount(**in2)

        parms = InactivateAccount(**inparms)

        self.assertTrue(isinstance(parms,InactivateAccount),
                        msg='constructor() failed');
        self.assertFalse('Nosuch' in parms, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = parms[key]
            self.assertEqual(val,expected_val)

class TestReactivateAccount(unittest.TestCase):
    def test_constructor(self):
        parm2type = ReactivateAccount.parm2type.copy()
        func_info = ReactivateAccount.__init__.func_info
        inkeys = func_info['allowed'].copy()
        inparms = {}
        for inkey in inkeys:
            inparms[inkey] = _make_test_value(parm2type,inkey)

        inkeys.append('Nosuch')
        parm2type['Nosuch'] = str

        reqparms = func_info['required'].copy()
        for reqparm in reqparms:
            in2 = inparms.copy()
            del in2[reqparm]
            with self.assertRaises(KeyError,
                                   msg=reqparm + " not required"):
                parms = ReactivateAccount(**in2)

        parms = ReactivateAccount(**inparms)

        self.assertTrue(isinstance(parms,ReactivateAccount),
                        msg='constructor() failed');
        self.assertFalse('Nosuch' in parms, msg='invalid key accepted')

        for key in func_info['allowed']:
            expected_val = _make_test_value(parm2type,key)
            val = parms[key]
            self.assertEqual(val,expected_val)


if __name__ == '__main__':
    unittest.main()
