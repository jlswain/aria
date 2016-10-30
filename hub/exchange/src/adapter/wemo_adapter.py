import uuid
import logging
import gevent
from adapter import Adapter
from ouimeaux.environment import Environment
from ouimeaux.signals import devicefound, statechange, receiver
from device import Device, DeviceType

logging.basicConfig(level=logging.DEBUG)


class WemoAdapter (Adapter):

    def __init__(self):
        super().__init__()
        self.env=Environment()
        self.deviceUids={}
        self.deviceNames={}
        # setup call back when device is discovered
        devicefound.connect(self._discovered)

    def setup(self):
        super().setup()
        self.env.start()
        #self.env.wait()

    def discover(self):
        self.env.discover()
        return True

    def _discovered(self,sender, **kwargs):
        uid = uuid.uuid4()

        self.deviceNames[uid] = sender.name
        self.deviceUids[sender.name]=uid
        print(sender)
        #deviceType = DeviceType(sender.name, False, 'WeMo')
        hostname=sender.services['basicevent'].hostname.split(':')
        address= (hostname[0],hostname[1])
        device=Device('wemo',sender.name,address)
        self.notify('discovered',device)
		
	def send (self, message):
		deviceName = self.deviceUIds[message.receiver]
		
		device = self.env.get(deviceName)
		
		#1 = ON  0 = OFF
		response = device.get_state()
		if device.get_state == 0:
			response = OFF
		elif device.get)state == 1:
			response == ON
		else:
			response == ERROR
		
		self.notify(Message(type = 3, data = { 'status' : response }, sender = message.receiver)
		
		
		
		

    def run(self):
        self.setup()
        self.discover()
        self.env.wait()
