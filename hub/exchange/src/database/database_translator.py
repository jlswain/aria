import logging
import sqlite3
from uuid import UUID

from adapter import Delegate, Message

log=logging.getLogger(__name__)

class DatabaseTranslator(Delegate):

    def __init__ (self, database):
       self.database = database 

    def received (self, message):
        if (message.type == Message.Request):
            log.info("Received " + str(message))
            return self._request(message)
        elif (message.type == Message.Event):
            self._event(message)
            
    def discovered (self, device):
        log.info('Received ' + str(device))
        sql = "INSERT INTO Device (address, version, name) VALUES (?, ?, ?)"
        self.database.execute(sql, (str(device.address), str(device.version), str(device.name)))  

    def _request(self, message):
        sql = "INSERT INTO Request (source, receiver, attribute, value) VALUES (?, ?, ?, ?)"
        values =  (self._getStr(message.sender), self._getStr(message.receiver), str(message.data['set']), str(message.data['value']))        
        self.database.execute(sql, values)
        results = self.database.execute
        return self.database.getLastInsertId()

    def _event(self, event):
        sql = "INSERT INTO Event (request_id, source, attribute, value) VALUES (?, ?, ?, ?)"
        id = message.data["requestId"] if "requestId" in message.data else None
        self.database.execute(sql, (id, self._getStr(message.sender), self._getStr(message.receiver)\
        , str(message.data['response']), str(message.data['value'])))

    def _getDeviceInfo(self, device):
        sql = "SELECT * FROM Device WHERE address = ?"
        return self.database.execute(sql, device)

    def _setDeviceName(self, name, device):
        sql = "UPDATE Device SET ? WHERE address = ?"
        self.database.execute(sql, (name, device))

    def _getStr(self, bytes_):
        return str(UUID(bytes = bytes_))
