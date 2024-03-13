#!/usr/bin/env python
import unittest
import json
from misctypes import DateTime
from amieparms import (AMIEParmDescAware, process_parms)

def upper(str):
    return str.upper()

class Target(AMIEParmDescAware):
    
    parm2type = {
        'name': str,
        'id': int,
        'timestamp': DateTime
    }
    parm2doc = {
        'name': 'myname',
        'id': 'myid',
        'timestamp': 'mytimestamp'
    }

    @process_parms(
        allowed=[
            'name',
            'id',
            'timestamp',
            'Comment',
        ],
        required=[
            'name',
            'id'
        ])
    def __init__(self,*args,**kwargs):
        """Test Target

        This is a dummy object for testing ParmDescAware
        :return: Nothing
        """

        self.args = args
        self.kwargs = kwargs


class TestParmDesc(unittest.TestCase):
    def test_init(self):
        inparms = {
            'name': 'myname',
            'id': 7,
            'timestamp': '2023-01-01T12:00:00-07:00',
            'Comment': 'defined in ParmDescAware',
            'extra': 'not used'
            }
        t = Target(**inparms)

        self.assertTrue(isinstance(t,Target),
                        msg='Constructor failed')
        args = t.args
        kwargs = t.kwargs

        self.assertEqual(len(args),0,
                         msg='positional parms were passed in')
        self.assertTrue('name' in kwargs,
                         msg='name parm not set')
        self.assertEqual(kwargs['name'],'myname',
                         msg='name parm not set')
        self.assertEqual(kwargs['id'],7,
                         msg='id parm not set')
        self.assertEqual(kwargs['timestamp'],'2023-01-01T12:00:00-07:00',
                         msg='timestamp parm not set')
        self.assertTrue(isinstance(kwargs['timestamp'],DateTime),
                         msg='timestamp parm not a DateTime instance')
        self.assertEqual(kwargs['Comment'],'defined in ParmDescAware',
                         msg='Inherited Comment parm not set')
        self.assertFalse('extra' in kwargs,
                         msg='extra parm passed in')

        init_doc = Target.__init__.__doc__

        expected_doc = "Test Target\n" + \
            "\n" + \
            "        This is a dummy object for testing ParmDescAware\n" + \
            "\n" + \
            "        :param name: myname\n" + \
            "        :type name: str\n" + \
            "        :param id: myid\n" + \
            "        :type id: int\n" + \
            "        :param timestamp: mytimestamp\n" + \
            "        :type timestamp: DateTime, optional\n" + \
            "        :param Comment: (Unknown)\n" + \
            "        :type Comment: str, optional\n" + \
            "        :return: Nothing"

        self.assertEqual(init_doc,expected_doc,
                         msg="__init__ docstring not supplemented")
        
if __name__ == '__main__':
    unittest.main()
