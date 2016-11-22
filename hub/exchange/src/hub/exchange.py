from .cli import CLI
from adapter import Message
import logging
from uuid import UUID
from database import DatabaseTranslator
from threading import Lock
from sync import synchronized

log =logging.getLogger(__name__)

lock = Lock()

class Exchange ():

    def __init__ (self, hub, cli, database):
        self._hub       = hub
        self._cli       = cli
        self._adapters  = {}
        self._devices   = {}
        self._database  = DatabaseTranslator(database)

    @synchronized(lock)
    def start (self):
        for _, adapter in self._adapters.items():
            log.debug('Starting adapter: ' + str(adapter))
            adapter.start()
 
    @synchronized(lock)
    def register (self, device_type, adapter):
        log.info('Registered adapter: ' + str(adapter))
        adapter.add_delegate(self)
        adapter.add_delegate(self._database)
        self._adapters[device_type] = adapter

    @synchronized(lock)
    def send (self, device, message):
        # TODO Log sending a message here
        if (device.deviceType.protocol in self._adapters):
            log.info('Sending ' + str(message) + ' to device ' + str(device))
            self._adapters[device.deviceType.protocol].send(message)

    @synchronized(lock)
    def teardown (self):
        for _, adapter in self._adapters.items():
            log.debug('Tearing down adapter: ' + str(adapter))
            adapter.teardown() 

    def received (self, message):
        log.info('Received ' + str(message))
        if( 'action' in message.data and message.data['action'] == 'discover'):
            self.send(self._devices[message.sender],Message(
                type_=Message.Ack,
                data={'success':'True'},
                receiver=message.sender))
            self.discoverDevices()
        elif (message.receiver in self._devices):
            log.debug('Routing message to ' + str(UUID(bytes=message.receiver)))
            self.send(self._devices[message.receiver], message)
            log.debug('Done routing message')

    def discoverDevices(self):
        for _, adapter in self._adapters.items():
            adapter.discover()

    @synchronized(lock)
    def discovered (self, device):
        log.info('Discovered device: ' + str(device))
        self._devices[device.address] = device
        # add device to hub
        self._hub.addDevice(device) 
