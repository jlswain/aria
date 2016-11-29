from unittest import TestCase
import unittest
from hub        import Hub, Exchange, CLI, args, daemon
from device     import Device,DeviceType, Attribute, DataType 
from ipc import Message
from adapter import Adapter
from database import Database
from delegate import RequestTracker
import queue
import sqlite3
import os
import uuid
import time
import json
import logging
import traceback
import threading
from uuid import UUID
from adapter import HubAdapter

logging.disable(logging.WARNING)
log=logging.getLogger(__name__)
class TestDatabaseIntegration(TestCase):

    @classmethod
    def setUpClass(self):
        self.devices = [Device(DeviceType("testname", "stub", "nobody", attributes=[Attribute('state',DataType.Binary)])) for i in range(0,20)]

    def registerFakeDevices(self):
        for device in self.devices:
            self.exchange.discovered(device)
            
    def setUp(self):

        try:
            os.remove(self._testMethodName + ".db")
        except OSError as e:
            pass

        self.database    = Database(self._testMethodName + ".db")
        self.hub         = Hub(self.database)
        self.cli         = CLI(self.hub)
        self.exchange    = Exchange(self.hub, self.cli, self.database)
        self.testAdapter = StubDeviceAdapter()
        self.exchange.register('stub', self.testAdapter)
        self.exchange.register('hub',HubAdapter(self.hub))
        self.exchange.discovered(self.hub)
        self.registerFakeDevices()
        self.exchange.start()

        self.db = TestDatabase(self._testMethodName + ".db")

    def tearDown(self):
        self.exchange.teardown()
        if (self.testAdapter.exceptionTrace):
           raise Exception(self.testAdapter.exceptionTrace)
        
    def test_sensor_event_message_should_be_logged_to_database(self):
        myUuid = self.devices[0].address
 
        sensorStateChangeMessage = Message()
        sensorStateChangeMessage.type = Message.Event
        sensorStateChangeMessage.sender = myUuid
        sensorStateChangeMessage.data = {"response" : "state", "value" : 1}

        self.testAdapter.enqueueMessage(sensorStateChangeMessage)
        self.exchange.teardown()
        results = self.db.query("SELECT * FROM Event").fetchone()
        self.assertEqual(results["request_id"], 1)
        self.assertEqual(results["source"], str(UUID(bytes=myUuid)))
        self.assertEqual(results["attribute"], "state")
        self.assertEqual(results["value"], "1")

    def test_requests_to_hub_should_not_be_logged_to_database(self):
        sensorStateChangeMessage = Message()
        sensorStateChangeMessage.type = Message.Request
        sensorStateChangeMessage.sender = self.devices[0].address

        sensorStateChangeMessage.data = {"set" : "mode", "value" : 2}
        self.testAdapter.enqueueMessage(sensorStateChangeMessage)
        self.exchange.teardown()
 

        results = self.db.query("SELECT count(*) as count FROM Event")
        self.assertEqual(results.fetchone()["count"], 0)


    def test_events_should_be_linked_to_requests(self):

        myUuid = self.devices[0].address
        requestMessage = Message()
        requestMessage.type = Message.Request
        requestMessage.data = {"set" : "brightness", "value" : 100}
        requestMessage.receiver = myUuid
        self.testAdapter.enqueueMessage(requestMessage)
        
        eventMessage = Message()
        eventMessage.data = { "response" : "brightness", "value" : 100 }
        eventMessage.type = Message.Event 
        eventMessage.sender = myUuid
        eventMessage.receiver = Message.DEFAULT_ADDRESS
        self.testAdapter.enqueueMessage(eventMessage)    
        time.sleep(1)
        self.exchange.teardown()

        results = self.db.query("SELECT count(*) as count FROM \
                                Event e INNER JOIN Request r ON e.request_id = r.id\
                                WHERE e.attribute = 'brightness' AND e.value = 100")

        firstResult = results.fetchone()
        self.assertEqual(firstResult['count'], 1)

    def test_request_event_window_returns_events(self):
        # Put twenty events in the database
        for device in self.devices:
            sensorStateChangeMessage = Message()
            sensorStateChangeMessage.type = Message.Event
            sensorStateChangeMessage.data = {"response" : "state", "value" : 1}
            sensorStateChangeMessage.sender = device.address
            self.testAdapter.enqueueMessage(sensorStateChangeMessage)

        # Give some time to write to database
        time.sleep(0.5)

        # Request the last 10 events that occurred
        sensorEventWindowRequest = Message()
        sensorEventWindowRequest.type = Message.Request
        sensorEventWindowRequest.data = {"get": "eventWindow", "start": 0, "count": 10}
        sensorEventWindowRequest.sender = self.devices[0].address
        self.testAdapter.enqueueMessage(sensorEventWindowRequest)

        # Give some time for the hub to respond to the request
        time.sleep(10)
        
        response = self.testAdapter.receivedMessages[0]
        
        self.assertEqual(response.data["response"], "eventWindow")
        self.assertEqual(response.data["value"]["total"], 10)
        self.assertEqual(len(response.data["value"]["records"]), 10)        

    def test_request_event_window_ignores_specified_devices(self):
        # Send a bunch of events from random devices
        for device in self.devices:
            sensorStateChangeMessage = Message()
            sensorStateChangeMessage.type = Message.Event
            sensorStateChangeMessage.data = {"response" : "state", "value" : 1}
            sensorStateChangeMessage.sender = device.address
            self.testAdapter.enqueueMessage(sensorStateChangeMessage)

        # Give some time to write to database
        time.sleep(0.5)

        # Request the last 10 events that occurred
        sensorEventWindowRequest = Message()
        sensorEventWindowRequest.type = Message.Request
        sensorEventWindowRequest.data = {"get": "eventWindow", "start": 0, "count": 20, "ignore" : [str(UUID(bytes=self.devices[0].address))]}
        sensorEventWindowRequest.sender = self.devices[0].address
        self.testAdapter.enqueueMessage(sensorEventWindowRequest)
        # Give some time for the hub to respond to the request
        time.sleep(10)

        response = self.testAdapter.receivedMessages[0]
        self.assertEqual(response.data["response"], "eventWindow")
        self.assertEqual(response.data["value"]["total"], 19)
        self.assertEqual(len(response.data["value"]["records"]), 19)
        for device in response.data["value"]["records"]:
            self.assertNotEqual(device["source"], str(self.devices[0].address))

class TestDatabase:

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.conn.row_factory = dict_factory
        self.conn.execute('pragma foreign_keys')
        self.cursor = self.conn.cursor()

    def query(self, sql):
        return self.cursor.execute(sql)



class StubDeviceAdapter(Adapter):

    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self.receivedMessages = []
        self.exceptionTrace = None

    def enqueueMessage(self, m):
        """
        Add a message to the queue of messages returned when receive() is called
        """
        self.q.put(m)

    def send(self, message):
        self.receivedMessages.append(message)

    def receive(self):
        try:
            """
            Pops the next message of the queue and notifies subscribers
            """
            message = self.q.get()
            if (message != None):
                self.notify('received', message)
            self.q.task_done()
            return True
        except:
            self.exceptionTrace = traceback.format_exc()
        return True

    def teardown(self):
        self.q.join()
        super().teardown()
        self.q.put(None)