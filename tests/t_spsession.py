#!/usr/bin/env python
import unittest
from datetime import (datetime, timedelta)
from misctypes import (DateTime, TimeUtil)
from retryingproxy import (RetryingServiceProxyError, RetryingServiceProxy)
from serviceprovider import (SPSession, ServiceProviderError,
                             ServiceProviderTimeout,
                             ServiceProviderTemporaryError,
                             ServiceProviderRequestFailed)

class MockTimeUtil(TimeUtil):
    def __init__(self):
        self.currtime = datetime.fromisoformat("1970-01-01T00:00:00+00:00")
        self.basetime = self.currtime
        self.sleep_arg = None
        self.called_sleep = False
        self.called_now = False

    def sleep(self, secs):
        self.currtime += timedelta(seconds=secs)
        self.sleep_arg = secs
        self.called_sleep = True

    def now(self):
        self.called_now = True
        return self.currtime

    def clear(self):
        self.sleep_arg = None
        self.called_sleep = False
        self.called_now = False

class MockServiceProvider(object):
    def dotest(self, exc=None):
        if exc is not None:
            raise exc()

class TestSPSession(unittest.TestCase):
    def setUp(self):
        self.timeutil = MockTimeUtil()
        self.sp = MockServiceProvider()
        SPSession.configure(sp=self.sp,
                            min_retry_delay=1, max_retry_delay=30,
                            retry_time_max=90,
                            time_util=self.timeutil)

    def test_configure(self):
        SPSession.configure(sp=None,
                            min_retry_delay=1, max_retry_delay=30,
                            retry_time_max=90)
        cls = SPSession
        self.assertEqual(cls.svc,None,
                         msg="svc set")
        self.assertEqual(cls.min_retry_delay,1,
                         msg="min_retry_delay not set")
        self.assertEqual(cls.max_retry_delay,30,
                         msg="max_retry_delay not set")
        self.assertEqual(cls.retry_time_max,90,
                         msg="retry_time_max not set")
        self.assertTrue(isinstance(cls.time_util,TimeUtil),
                        msg="default time_util set")


        SPSession.configure(sp=MockServiceProvider(),
                            min_retry_delay=1, max_retry_delay=30,
                            retry_time_max=90,
                            time_util=self.timeutil)
        self.assertTrue(isinstance(cls.svc,MockServiceProvider),
                        msg="svc not set")
        self.assertTrue(isinstance(cls.time_util,MockTimeUtil),
                        msg="explicit time_util not set")

        
    def test_no_temp_errors(self):
        sps = SPSession
        with sps() as sp:
            sp.dotest()

        self.assertEqual(sps.retry_delay,None,
                         msg="after clear run, sps has retry_delay value")
        self.assertEqual(sps.retry_deadline,None,
                         msg="after clean run, sp has retry_deadline value")

        self.assertFalse(self.timeutil.called_sleep,
                         msg="sleep() called in clean run")
        self.assertFalse(self.timeutil.called_now,
                         msg="now() called in clean run")


    def test_ServiceProviderTemporaryError(self):
        wrong_retry_delay_msg="after temp err, wrong retry_delay value"
        wrong_retry_deadline_msg="after temp err, wrong retry_deadline value"
        sps = SPSession
        spsi = sps()
        with self.assertRaises(ServiceProviderTemporaryError,
                               msg="TemporaryError not propagated"):
            with spsi as sp:
                sp.dotest(ServiceProviderTemporaryError)

        self.assertEqual(sps.retry_delay,1,
                         msg=wrong_retry_delay_msg)
        expected_deadline = self.timeutil.basetime + timedelta(seconds=90)
        self.assertEqual(sps.retry_deadline,expected_deadline,
                         msg=wrong_retry_deadline_msg)

        self.assertFalse(self.timeutil.called_sleep,
                         msg="sleep() called after first tmp err")
        self.assertTrue(self.timeutil.called_now,
                         msg="now() not after tmp err")
        self.timeutil.clear()

        for sa in (1,2,4,8):
            new_delay = sa * 2
            
            with self.assertRaises(ServiceProviderTemporaryError,
                                   msg="TemporaryError not propagated"):
                with spsi as sp:
                    sp.dotest(ServiceProviderTemporaryError)

            self.assertEqual(sps.retry_delay,new_delay,
                             msg=wrong_retry_delay_msg)
            self.assertEqual(sps.retry_deadline,
                             expected_deadline,
                             msg=wrong_retry_deadline_msg)
            
            self.assertTrue(self.timeutil.called_sleep,
                            msg="sleep() called after first tmp err")
            self.assertEqual(self.timeutil.sleep_arg, sa,
                             msg="sleep() called with wrong value")
            self.assertTrue(self.timeutil.called_now,
                            msg="now() not after tmp err")
            self.timeutil.clear()

        for sa in (16,30):
            with self.assertRaises(ServiceProviderTemporaryError,
                                   msg="TemporaryError not propagated"):
                with spsi as sp:
                    sp.dotest(ServiceProviderTemporaryError)

            self.assertEqual(sps.retry_delay,30,
                             msg=wrong_retry_delay_msg)
            self.assertEqual(sps.retry_deadline,
                             expected_deadline,
                             msg=wrong_retry_deadline_msg)

            self.assertTrue(self.timeutil.called_sleep,
                            msg="sleep() called after first tmp err")
            self.assertEqual(self.timeutil.sleep_arg, sa,
                             msg="sleep() called with wrong value")
            self.assertTrue(self.timeutil.called_now,
                            msg="now() not after tmp err")
            self.timeutil.clear()

        with self.assertRaises(ServiceProviderTimeout,
                               msg="timeout exceeded error not raised"):
            with spsi as sp:
                sp.dotest(ServiceProviderTemporaryError)

        self.assertEqual(sps.retry_delay,None,
                         msg=wrong_retry_delay_msg)
        self.assertEqual(sps.retry_deadline,None,
                         msg=wrong_retry_deadline_msg)

        self.assertTrue(self.timeutil.called_sleep,
                        msg="sleep() called after first tmp err")
        self.assertEqual(self.timeutil.sleep_arg, 30,
                         msg="sleep() called with wrong value")
        self.assertTrue(self.timeutil.called_now,
                        msg="now() not after tmp err")
        self.timeutil.clear()
        
        
if __name__ == '__main__':
    unittest.main()
