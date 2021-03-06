import sqlite3
import logging
from device import DataType
log = logging.getLogger(__name__)

class Retriever:

    GET_BEHAVIOUR_WINDOW    = "SELECT id, name, created_date, last_updated, active FROM Behaviour \
                               ORDER BY id DESC LIMIT ?,?" 
    GET_SESSIONS_WINDOW      = "SELECT * FROM session WHERE behaviour_id = ? \
                                ORDER BY id DESC LIMIT ?,?"
    GET_ALL_EVENT_WINDOW    = "SELECT id as 'index', timestamp, source \
                               FROM Event ORDER BY id DESC LIMIT ?,?"
    GET_DEVICE_EVENT_WINDOW = "SELECT * FROM Event WHERE source = ? LIMIT  ?,?"
    GET_PARAM_CHANGE        = "SELECT parameter, value FROM Parameter_Change WHERE event_id = ?"
    GET_PARAM_INFO          = "SELECT name, data_type, attribute_id FROM Parameter WHERE id = ?" 
    GET_DEVICE_TYPE         = "SELECT type, name FROM Device WHERE address = ?"
    GET_ATTRIBUTE_NAME      = "SELECT name FROM Attribute WHERE id = ?"
    GET_SESSION             = "SELECT * from session where id=?"
    GET_LAST_EVENT_ID       = "SELECT id FROM Event ORDER BY id DESC LIMIT 1 "
    GET_LAST_BEHAVIOUR      = "SELECT * FROM Behaviour ORDER BY id DESC LIMIT 1 "
    GET_LAST_SESSION        = "SELECT * FROM Session ORDER BY id DESC LIMIT 1 "
    GET_BEHAVIOUR           = "SELECT * FROM Behaviour where id= ?"

    ADD_NEW_BEHAVIOUR       = "INSERT INTO Behaviour (name) VALUES (?)"
    ADD_NEW_SESSION         = "INSERT INTO Session (behaviour_id, name) VALUES (?, ?)"
    GET_SESSION_EVENTS      = 	"SELECT e.id, " +\
	                            " e.timestamp, " +\
	                            " e.source, " +\
	                            " p.NAME as parameter_name, " +\
	                            " pc.value, " +\
	                            " e.request_id, " +\
                                " a.name as attribute_name, " +\
                                " s.behaviour_id " +\
	                            "FROM   event e " +\
	                            "  JOIN parameter_change pc " +\
	                            "    ON e.id = pc.event_id " +\
	                            "  JOIN parameter p " +\
	                            "    ON p.id = pc.parameter " +\
                                "  JOIN attribute a on a.id = p.attribute_id "+\
                                "  JOIN session s on e.session_id= s.id "+\
	                            " WHERE  session_id = ? order by e.timestamp ASC"
    STOP_SESSION            = "UPDATE session set stopped = 1 where id=?"  
    DELETE_BEHAVIOUR        = "DELETE FROM behaviour where id=?"
    DELETE_SESSION          = "DELETE FROM session where id=?"
    def __init__(self, database):
        self.database = database																									

    def retriable(operation):
        def wrapper(*args, **kwargs):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                log.exception(e)
                return operation(*args, **kwargs)
        return wrapper

    ###
    # Get a list of count events across all devices
    # @param start   Index in the database to start retrieving from, with 0 being the most recent
    #                record
    # @param count   Number of events to retrieve
    # @param ignore  List of device UUIDs that should be ignored when retrieving events
    #
    # @return        List of count number of event objects across all devices
    ###
    @retriable
    def getEventWindow(self, start, count):
        values = (start, count)
        results = self.database.execute(Retriever.GET_ALL_EVENT_WINDOW, values)
        for r in results:
            device = self._getDeviceType(r["source"])

            r['device']= device[0]['name']
            params = self._getParametersChanged(r["index"])

            r["attribute"] = {}
            r["attribute"]["parameters"] = []
            
            for p in params:
                newParam = {}
                paramInfo = self._getParameterInfo(p["parameter"])
                newParam["value"] = p["value"]
                newParam["name"] = paramInfo[0]['name']
                newParam["dataType"] = DataType(paramInfo[0]['data_type'])
                r["attribute"]["parameters"].append(newParam)
            
            r["attribute"]["name"] = self._getAttributeName(paramInfo[0]['attribute_id'])[0]['name']
            
        return results

    ###
    # Get a list of count events for a specific device
    # @param id      UUID of the device to get events from 
    # @param start   Index in the database to start retrieving from, with 0 being the most recent
    #                record
    # @param count   Number of events to retrieve
    #
    # @return        List of count number of event objects for the specified device id
    ###
    def getDeviceEvents(self, id_, start, count):
        lastEventId = self.database.execute(Retriever.GET_LAST_EVENT_ID)
        values = (id_, start,count)
        results = self.database.execute(Retriever.GET_ALL_EVENT_WINDOW, values)
        return results

    ###
    # Add a new behaviour
    # @param name    Name of the new behaviour
    #
    # @return        The newly created behaviour
    ###
    def addBehaviour(self, name):
        self.database.execute(Retriever.ADD_NEW_BEHAVIOUR, [name])
        return self.database.execute(Retriever.GET_LAST_BEHAVIOUR)[0]

    ###
    # Add a new session
    # @param name    Name of the new session
    #
    # @return        The newly created session
    ###
    def addSession(self,behaviourId, name):
        values = (behaviourId, name) 
        self.database.execute(Retriever.ADD_NEW_SESSION, values)
        return self.database.execute(Retriever.GET_LAST_SESSION)[0]

    ###
    # @param id     the id of the session
    #
    # @return       A single session
    def getSession(self,id_):
        return self.database.execute(Retriever.GET_SESSION, [id_])[0]

    ###
    # Get a list of count behaviours
    # @param start   Index in the database to start retrieving from, with 0 being the most recent
    #                record
    # @param count   Number of behaviours to retrieve
    #
    # @return        List of count number of event objects across all devices
    ###
    def getBehaviourWindow(self, start, count):
        values = (start, count)
        return self.database.execute(Retriever.GET_BEHAVIOUR_WINDOW, values)

    ###
    # Get a list of count training sessions for a behaviour
    # @param start        Index in the database to start retrieving from, with 0 being the most recent
    #                     record
    # @param count        Number of sessions to retrieve
    # @param behaviourId  The behaviour to retrieve training sessions from
    #
    # @return        List of count number of event objects across all devices
    ###
    def getSessionsWindow(self, start, count, behaviourId):
        values = (behaviourId,start, count)
        return self.database.execute(Retriever.GET_SESSIONS_WINDOW, values)

    def getSessionEvents(self,session_id):
        """
        Get a list of events associated with a training session
            
        @param session_id   The id of the session 
        """
        return self.database.execute(Retriever.GET_SESSION_EVENTS, [session_id])

    def updateBehaviour(self,id_, name,active):
        if  name == None and active == None:
            return self.database.execute(Retriever.GET_BEHAVIOUR,[id_])[0]
        params={}
        params['name']=name
        params['active']=active
        sql="Update behaviour set %s where id=?" %(
            ','.join('%s=?'% p for p, val  in params.items() if val != None ))
        self.database.execute(sql,[v for v in params.values() if v != None]+[id_])
        return self.database.execute(Retriever.GET_BEHAVIOUR,[id_])[0]
        


    def stopSession(self,session_id):
        self.database.execute(Retriever.STOP_SESSION,[session_id])

    def deleteBehaviour(self,behaviour_id):
        self.database.execute(Retriever.DELETE_BEHAVIOUR,[behaviour_id])
        
    def deleteSession(self,session_id):
        self.database.execute(Retriever.DELETE_SESSION,[session_id])

    def _getAttribute(self, deviceType):
        return self.database.execute(Retriever.GET_ATTRIBUTE_ID, [deviceType])

    def _getAttributeName(self, attributeID):
        return self.database.execute(Retriever.GET_ATTRIBUTE_NAME, [attributeID])

    def _getDeviceType(self, address):
        return self.database.execute(Retriever.GET_DEVICE_TYPE, [address])

    def _getParametersChanged(self, eventID):
        return self.database.execute(Retriever.GET_PARAM_CHANGE, [eventID])

    def _getParameterInfo(self, paramID):
        return self.database.execute(Retriever.GET_PARAM_INFO, [paramID])
