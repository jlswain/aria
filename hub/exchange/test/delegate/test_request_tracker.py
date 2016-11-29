import uuid
import json
from unittest import TestCase
from unittest.mock import Mock,patch
from device import Device, DeviceType,Attribute,DataType
from hub import Hub
from database import RequestTracker
from ipc import Message


class RequestTrackerTest(TestCase):

    def setUp(self):
        self.id=uuid.uuid4().bytes        
        self.dev=Device(DeviceType('WeMo Switch','wemo', maker='WeMo', \
        attributes=[Attribute('state',DataType.Binary)]), name= 'Lamp Switch', address=self.id,\
         version='0.1.0')
        self.hub=Hub()


    @patch('database.DatabaseTranslator')       
    def test_ignore_message(self,MockTranslator):
        MockTranslator.received.return_value=True
        tracker=RequestTracker(MockTranslator, self.hub)
        # test ignore unkown sender
        self.assertFalse(tracker.received(Message(Message.Request,sender=uuid.uuid4().bytes,\
        receiver=self.id)))
        self.hub.addDevice(self.dev)
        # test ignore request for hub
        self.assertFalse(tracker.received(Message(Message.Request,sender=self.id)))
    
    @patch('database.DatabaseTranslator')
    def test_request(self,MockTranslator):

        def receive(message):
            self.assertTrue(message.type == Message.Request)
       
        MockTranslator.received=receive
        tracker=RequestTracker(MockTranslator, self.hub)
        self.hub.addDevice(self.dev)
        tracker.received(Message(Message.Request,\
            sender=self.id,receiver=uuid.uuid4().bytes))

        
    @patch('database.DatabaseTranslator')
    def test_create_request(self,MockTranslator):

        def receive(message):
            if (message.type == Message.Request):
                return 10
            elif (message.type == Message.Event):
                self.assertTrue('requestId' in message.data)
                
        MockTranslator.received=receive

        self.hub.addDevice(self.dev)
        tracker=RequestTracker(MockTranslator, self.hub)
        tracker.received(Message(Message.Event, data={'response':'state', 'value':0},\
            sender=self.id,receiver=uuid.uuid4().bytes))
        
        self.assertEqual(tracker.requests.get(self.dev.address),10)

         

