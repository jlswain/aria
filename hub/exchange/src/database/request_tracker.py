import logging
from adapter import Message
from database import DatabaseTranslator 

log= logging.getLogger(__name__)


class RequestTracker(DatabaseTranslator):

    def __init__(self,databaseTranslator,hub):
        self.dbTranslator=databaseTranslator
        self.requests={}
        self.hub=hub

    def received(self,message):
        """
            decorates the receive of database translator to assosiate a request to a device
            with an event/response from a device. If a previous request doesn't exist
            for a device then this was a manual user action, a request is created for this 
            action.
        """
        device= self.hub.getDevice(message.sender)
        if(not device):
            log.warn('Unknown sender')
            return False
        # ignore requests to hub they don't need to be logged
        if(Message.Request == message.type and message.receiver != self.hub.address):
            self.requests[message.receiver]=self.databaseTranslator.received(message)
        elif(Message.Event == message.type or Message.Response == message.type):
            reqid=self.requests.pop(message.receiver,None)
            # don't create a request for a non controllable device
            if(reqid or not device.deviceType.isControllable):
                self.sendEvent(reqid,message)
            else:
                try:
                    msg=self.createRequest(message)
                    reqid=self.databaseTranslator.received(msg)
                    self.sendEvent(reqid,message)
                except:
                    log.warn('Invalid Event message '+message)
        else:
            self.databaseTranslator.received(message)
        
        
        def sendEvent(self,reqid,message):
            if(reqid):
                message.data['requestId']= reqid
            self.databaseTranslator.received(message)
        
        def createRequest(self,message):
            # Event messages have the form {'response':<Atribute>, 'value':<value>}
            # Requests have the form {'set':<attribute>, 'value':<value> }
            data={'set':message.data['response'],'value':message.data['value']}
            return Message(type_=Message.Request,data=data,receiver=message.sender)

            
