### J-2 Database Interface {- #J-2}

#### General {-}

This interface provides a way for components in our system to query the database using the defined
methods. Any component which has an instance of the Retriever class has access to these methods. 
A combination of prepared statements and having the database only accessed through an instance of
Retriever eliminates the possibility of SQL injection, protecting our system.

#### Setup Instructions {-}

To test this interface, there must be an existing database populated with event records. 
Accomplishing this through our system is a fairly comprehensive task. A database can be created by
passing the desired name to the Database class. The created database will initially be empty. To
populate it, devices must be created and registered to the hub. Events then need to be generated 
from these devices, sent through the system, and logged in the database. At this point, this 
interface is ready to be tested.

An alternative to this is to create and populate a test database manually. An instance of Retriever 
could be contained by a stubbed component and this interface could then be tested.

#### Interface Documentation {-}

##### Event Window {-}

+---------------+-------------------------------------------------------------------------------+
| Title     	| **Get Recent Events Across All Devices in a Window**	       					|
|      		 	|                                                                             	|
|       		| Allows the retrival of a list of events starting from a specified index,		|
|				| ignoring events from specific devices if desired.								|
+---------------+-------------------------------------------------------------------------------+
| Data Params	| - **start** *<int>*: Index in the database to start retrieving from, with 0 	|
|				|	being the most recent record												|
| 				| - **count** *<int>*: Number of events to retrieve								|
| 				| - **ignore** *<list>*: A list of device UUID's. Any events generated by a 	|
|				| device with a UUID in this list will be ignored.								|
+---------------+-------------------------------------------------------------------------------+
| Sample		| - **type** *<list>*: List of dictionaries representing table records 			|
| Response		| 																				|
|				|																				|
| 				|			[																	|
|				|				{ 																|
| 				|					"id" 		: 2,											|	
| 				|					"timestamp" : "2016-11-26 22:59:52",						|
| 				|					"request" 	: 3,											|
| 				|					"source" 	: "123e4567-e89b-12d3-a456-426655440000",		|
| 				|					"change" 	: {												|
| 				|						"id" 		: 4,										|
|				|						"parameter" : {											|
|				|							"id" 		: 2,									|
|				|							"attribute"	: 18,									|
|				|							"data_type"	: "color"								|
|				|						},														|
|				|						"value" : "#F5F6AC"										|
|				|					}															|
| 				|				}																|
|				|				...																|
|				|			]																	|
+---------------+-------------------------------------------------------------------------------+
| Sample Call	| `getEventWindow(5, 10, [])`													|
+---------------+-------------------------------------------------------------------------------+


##### Device Events {-}

+---------------+-------------------------------------------------------------------------------+
| Title     	| **Get Recent Events for One Device in a Window**	       						|
|      		 	|                                                                             	|
|       		| Allows the retrival of a list of events starting from a specified index,		|
|				| ignoring events from specific devices if desired.								|
+---------------+-------------------------------------------------------------------------------+
| Data Params	| - **id** *<string>*: UUID of device to get events from						|
|				| - **start** *<int>*: Index in the database to start retrieving from, with 0 	|
|				|	being the most recent record												|
| 				| - **count** *<int>*: Number of events to retrieve								|
+---------------+-------------------------------------------------------------------------------+
| Sample		| - **type** *<list>*: List of dictionaries representing table records 			|
| Response		| 																				|
|				|																				|
| 				|			[																	|
|				|				{ 																|
| 				|					"id" 		: 2,											|	
| 				|					"timestamp" : "2016-11-26 22:59:52",						|
| 				|					"request" 	: 3,											|
| 				|					"source" 	: "123e4567-e89b-12d3-a456-426655440000",		|
| 				|					"change" 	: {												|
| 				|						"id" 		: 4,										|
|				|						"parameter" : {											|
|				|							"id" 		: 2,									|
|				|							"attribute"	: 18,									|
|				|							"data_type"	: "color"								|
|				|						},														|
|				|						"value" : "#F5F6AC"										|
|				|					}															|
| 				|				}																|
|				|				...																|
|				|			]																	|
+---------------+-------------------------------------------------------------------------------+
| Sample Call	| `getDeviceEvents("123e4567-e89b-12d3-a456-426655440000", 10, 5)`				|
+---------------+-------------------------------------------------------------------------------+
