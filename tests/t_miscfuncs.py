#!/usr/bin/env python
import pprintpp
pprintpp.monkeypatch()
import pprint
import unittest
from miscfuncs import (truthy, pformat, to_expanded_string)
import miscfuncs

class TestData(object):
    def __init__(self):
        self.foo = 'bar'
    
class TestTruthy(unittest.TestCase):

    def test_truthy(self):
       self.assertTrue(truthy(True),
                        msg='truthy(True) is false');
       self.assertTrue(truthy(1),
                        msg='truthy(1) is false');
       self.assertTrue(truthy("1"),
                        msg='truthy("1") is false');
       self.assertTrue(truthy("true"),
                        msg='truthy("true") is false');
       self.assertTrue(truthy("TRUE"),
                        msg='truthy("TRUE") is false');
       self.assertTrue(truthy([0]),
                        msg='truthy([0]) is false');
       self.assertTrue(truthy({"":0}),
                        msg='truthy({"":0}) is false');
       self.assertFalse(truthy(""),
                        msg='truthy("") is true');
       self.assertFalse(truthy(0),
                        msg='truthy(0) is true');
       self.assertFalse(truthy([]),
                        msg='truthy([]) is true');
       self.assertFalse(truthy({}),
                        msg='truthy({}) is true');
       self.assertFalse(truthy("0"),
                        msg='truthy("0") is true');
       self.assertFalse(truthy("false"),
                        msg='truthy("false") is true');
       self.assertFalse(truthy("FALSE"),
                        msg='truthy("FALSE") is true');
       self.assertFalse(truthy("f"),
                        msg='truthy("") is true');
       self.assertFalse(truthy("F"),
                        msg='truthy("F") is true');
       self.assertFalse(truthy("no"),
                        msg='truthy("no") is true');
       self.assertFalse(truthy("NO"),
                        msg='truthy("NO") is true');
       self.assertFalse(truthy("n"),
                        msg='truthy("n") is true');
       self.assertFalse(truthy("N"),
                        msg='truthy("N") is true');

    def test_pformat(self):
        self.assertEqual(pformat(None),"None",
                         msg='pformat(None) does not return expected string')
        
        self.assertEqual(pformat("foo"),"'foo'",
                         msg="pformat(str) does not return 'str'")

        td = TestData()
        tds = pformat(td)
        self.assertEqual(tds[0:29],"<__main__.TestData object at ",
                         msg='pformat(obj) does not return expected string')

    def test_to_expanded_string(self):
        self.assertEqual(to_expanded_string(None),"(None)",
                         msg='to_expanded_string(None) does not return expected string')
        
        self.assertEqual(to_expanded_string("foo"),"foo",
                         msg="to_expanded_string(str) does not return 'str'")

        td = TestData()
        tds = to_expanded_string(td)
        self.assertEqual(tds[0:29],"<__main__.TestData object at ",
                         msg='pformat(obj) does not return expected string')
        self.assertEqual(tds[-14:],"{'foo': 'bar'}",
                         msg='to_expanded_string(obj) does not return expected string')

        xml = "<html><body></body></html>"
        xmls = to_expanded_string(xml)
        self.assertEqual(xmls,"<html>\n  <body />\n</html>",
                         msg='pformat(xml) does not return expected string')

if __name__ == '__main__':
    unittest.main()
