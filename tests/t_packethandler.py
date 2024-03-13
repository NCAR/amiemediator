#!/usr/bin/env python
import unittest

from amieclient.packet.base import Packet
from amieclient.packet.project import RequestProjectCreate
from fixtures.request_project_create import RPC_PKT_1
from test.test_sp import ServiceProvider as TestServiceProvider
from packethandler import (PacketHandlerError,
                           PacketHandler,
                           ServiceProviderAdapter)

class MockHandler(PacketHandler, packet_type="request_project_create"):
    def __init__(self):
        super().__init__()
        self.counter = 3
        
    def work(self):
        self.counter -= 1
        return (self.counter > 0)
    
class TestPacketHandler(unittest.TestCase):
    def setUp(self):
        self.sp = TestServiceProvider()
        self.packet = Packet.from_dict(RPC_PKT_1)
        
    def test_constructor(self):

        handler = MockHandler()

        self.assertTrue(isinstance(handler,MockHandler),
                        msg="constructor failed")
        self.assertTrue(isinstance(handler.sp_adapter,ServiceProviderAdapter),
                         msg="handler sp_adapter not set")

        did_work = handler.work()
        self.assertTrue(did_work,
                        msg="run first iteration returned False")
        did_work = handler.work()
        self.assertTrue(did_work,
                        msg="run second iteration returned False")
        did_work = handler.work()
        self.assertFalse(did_work,
                        msg="run third iteration returned True")

if __name__ == '__main__':
    unittest.main()
