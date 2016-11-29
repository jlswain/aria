import json
import logging
import uuid
from .hub_mode  import HubMode
from device import Device, DeviceType, Attribute, DataType
from ipc import Message
from database import Retriever
from device import SoftwareDeviceFactory

log=logging.getLogger(__name__)

class Hub(Device):
    VERSION = '0.0.2'
    ADDRESS= Message.DEFAULT_ADDRESS
    GATEWAY_ADDRESS=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01' 
    
    def __init__ (self, database, args = {}, exit = None):
        # setup device attributes and DeviceType
        methods=[Attribute('name',DataType.String), Attribute('devices',DataType.List),\
         Attribute('mode',DataType.String)]
        devType=DeviceType('Hub','hub',attributes=methods)
        super().__init__(devType,'Smart Hub',Hub.ADDRESS, version= Hub.VERSION)
        self._devices = {}
        self.mode    = HubMode.Normal
        self.exit    = exit if exit else lambda: None
        self.retriever=Retriever(database)

    def getCommand (self, attribute,params=None):
        if attribute == 'status':
            return self.status()
        if attribute == 'devices':
            return self.getDevicesJson()
        if attribute == 'name':
            return self.name
        if attribute == 'mode':
            return self.mode.value
        if attribute == 'eventWindow':
            return self.getEventWindow(params)
        if attribute == 'deviceEvents':
            return self.getDeviceEvents(params)
        if attribute == 'softwareDevices' :
            return SoftwareDeviceFactory.getAvailableDevices()

    def setCommand (self, attribute,value):
        if attribute == 'name':
            self.name=value
            return self.name
        if attribute == 'mode':
            self.setMode(value)
            return self.mode.value
        if attribute == 'softwareDevices':
            print("VALUE " + str(value))
            device = SoftwareDeviceFactory.create(value)
            return 'true'

    def status (self):
        return {
            'version'   : self.version,
            'mode'      : self.mode.value,
            'devices'   : len(self._devices)
        }

    def getEventWindow(self,params):
        start=params['start']
        count=params['count']
        ignore=params.get('ignore','')
        if(ignore):
            ignore =",".join(ignore)
        results = self.retriever.getEventWindow(start,count,ignore)
        self.formatEvents(results)
        return {'total':len(results),'records':results}

    def getDeviceWindow(self,params):
        id_=params['id']
        start=params['start']
        count=params['count']
        results = self.retriever.getEventWindow(id_,start,count)
        return{'total':len(results),'records':results}
    
    def formatEvents(self,events):
        for event in events:
            device=self.getDevice(uuid.UUID(event['source']).bytes)
            attribute=device.getAttribute(event['attribute'])
            if(attribute):
                event['dataType']=attribute.dataType

    def addDevice (self,device):
       # don't add the hub or gateway to devices
        if(device == self):
            return
        elif (device.address == Hub.GATEWAY_ADDRESS):
            return
        log.debug('adding device '+str(device))
        self._devices[device.address]=device

    def getDevicesJson (self):
        data=list(self._devices.values())
        log.debug('sending device list '+ str(data))
        return data

    def setMode(self,mode):
        self.mode=HubMode(mode)

    def getDevice(self,address):
        return self if address == self.address else self._devices.get(address)