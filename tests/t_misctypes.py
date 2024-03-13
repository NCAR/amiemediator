#!/usr/bin/env python
import unittest
import json
from datetime import datetime
from datetime import tzinfo
from dateutil.parser import ParserError
from misctypes import DateTime

class TestDateTime(unittest.TestCase):
    def setUp(self):
        self.testtime_s = "2023-01-01T12:00:00-07:00"
        self.testtime = datetime.fromisoformat(self.testtime_s);
        self.testtimestamp = self.testtime.timestamp();

    def test_constructor(self):
       with self.assertRaises(ParserError,
                               msg="Invalid string accepted"):
           dt = DateTime("wtf")

       with self.assertRaises(TypeError,
                              msg="Single int arg accepted"):
           dt = DateTime(2023)

       dt = DateTime(self.testtime_s)

       self.assertEqual(dt,self.testtime_s,
                        msg='value from string wrong');

       dt = DateTime(self.testtime)

       self.assertEqual(dt,self.testtime_s,
                        msg='value from datetime wrong');

    def test_attrs(self):
       dts = DateTime(self.testtime_s)
       dt = dts.datetime()
       self.assertEqual(dt.year,self.testtime.year,
                        msg='year attr wrong');
       self.assertEqual(dt.month,self.testtime.month,
                        msg='month attr wrong');
       self.assertEqual(dt.day,self.testtime.day,
                        msg='day attr wrong');
       self.assertEqual(dt.hour,self.testtime.hour,
                        msg='hour attr wrong');
       self.assertEqual(dt.minute,self.testtime.minute,
                        msg='minute attr wrong');
       self.assertEqual(dt.second,self.testtime.second,
                        msg='second attr wrong');
       self.assertEqual(dt.isoformat(),self.testtime_s,
                        msg='iso string wrong');
       self.assertEqual(dts.timestamp(),self.testtimestamp,
                        msg='timestamp wrong')

        
if __name__ == '__main__':
    unittest.main()
