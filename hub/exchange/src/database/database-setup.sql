/*
id        --  auto incrementing integer key
timestamp --  date and time of the request
source    --  UUID of the sending device
receiver  --  UUID of the receiving device
*/
CREATE TABLE IF NOT EXISTS "Request" (
	"id" Integer PRIMARY KEY,
	"timestamp" DATETIME DEFAULT (datetime('now','localtime')),
	"source" TEXT,
	"receiver" TEXT,
	FOREIGN Key ("source") REFERENCES Device("address"),
	FOREIGN Key ("receiver") REFERENCES Device("address")
);

/*
id          --  auto incrementing integer key
timestamp   --  date and time of the request
request_id  --  id of request in Request table which caused the event, 0 if not caused by request
source      --  UUID of the sending device
session_id  --  id of the session if currently in a training session
*/
CREATE TABLE IF NOT EXISTS "Event" (
	"id" INTEGER PRIMARY KEY,
	"timestamp" DATETIME DEFAULT (datetime('now','localtime')),
	"request_id" INTEGER,
	"source" TEXT,	
	"session_id" INTEGER,
	FOREIGN KEY ("request_id") REFERENCES Request("id"),
	FOREIGN KEY ("source") REFERENCES Device("address"),
	FOREIGN KEY ("session_id") REFERENCES Session("id") ON DELETE CASCADE
);

/*
id         --  auto incrementing integer key
parameter  --  parameter that is being changed 
value      --  value the parameter is being changed to
event_id   --  id of event in Event table which cause the parameter change
*/
CREATE TABLE IF NOT EXISTS "Parameter_Change" (
	"id" INTEGER PRIMARY KEY,
	"parameter" INTEGER,
	"value" TEXT,
	"event_id" INTEGER,
	FOREIGN KEY ("parameter") REFERENCES Parameter("id"),
	FOREIGN KEY ("event_id") REFERENCES Event("id") ON DELETE CASCADE
);

/* 
id          --  auto incrementing integer key
name        --  user specified name of the device
protocol    --  specifies what adapter will be needed (Z-Wave, WeMo, etc)
maker       --  device company (Samsung, Aeon Labd, etc)
*/
CREATE TABLE IF NOT EXISTS "Device_Type" (
	"id" INTEGER PRIMARY KEY,
	"name" TEXT,
	"protocol" TEXT,
	"maker" TEXT
);

/*
address        --  UUID of device or sensor
version   --  firmware version of device 
type      --  type of the device
name      --  user specified name of device
*/
CREATE TABLE IF NOT EXISTS "Device" (
	"address" TEXT PRIMARY KEY ,
	"version" TEXT,
	"type" INTEGER,
	"name" TEXT,
	FOREIGN KEY("type") REFERENCES "Device_Type"("id")
);

/*
id            --  auto incrementing integer key
name          --  name of the attribute
device_type   --  type of device which has this attribute
controllable  --  0 if not controllable, 1 if controllable
*/
CREATE TABLE IF NOT EXISTS "Attribute" (
	"id" INTEGER PRIMARY KEY,
	"name" TEXT,
	"device_type" TEXT,
	"controllable" INTEGER,
	FOREIGN KEY ("device_type") REFERENCES "Device_Type"("id")
);

/*
id           --  auto incrementing integer key
name         --  name of parameter
attribute_id --  an id linking to an id in the Attributes table
data_type    --  the type of data returned when an attribute is performed
max          --  maximum value of an Integer value
min          --  minimum value of an Integer value
step         --  increment or decrement value
*/
CREATE TABLE IF NOT EXISTS "Parameter" (
	"id" INTEGER PRIMARY KEY,
	"name" TEXT,
	"attribute_id" INTEGER,
	"data_type" TEXT,
	"max" INTEGER,
	"min" INTEGER,
	"step" REAL,
	FOREIGN KEY ("attribute_id") REFERENCES "Attribute"("id")
);

/*
id          --  auto incrementing integer key
schedule_id --  link to a schedule in the Schedule table
parameter   --  parameter to be changed
value       --  value the parameter should be changed to
*/
CREATE TABLE IF NOT EXISTS "Scheduled_Change" (
	"id" INTEGER PRIMARY KEY,
	"schedule_id" INTEGER,
	"parameter" INTEGER,
	"value" TEXT,
	FOREIGN KEY ("schedule_id") REFERENCES "Schedule"("id")
);

/*
id        --  auto incrementing integer key
expire    --  date and time when the event is scheduled to occur
interval  --  how often the event should occur
repeat    --  0 if the event is not recurring, otherwise 1
*/
CREATE TABLE IF NOT EXISTS "Schedule" (
	"id" INTEGER PRIMARY KEY,
	"expire" DATETIME,
	"interval" DATETIME,
	"repeat" INTEGER
);

/*
id            -- auto incrementing integer key
name          -- name of the behaviour
created_date  -- timestamp of when the behaviour was created
last_updated  -- timestamp of the last time this behaviour was updated
active        -- is this behaviour enabled or is it disabled, defaults to enabled 
*/
CREATE TABLE IF NOT EXISTS "Behaviour" (
	"id" INTEGER PRIMARY KEY,
	"name" TEXT,
	"created_date" DATETIME DEFAULT (datetime('now','localtime')),
	"last_updated" DATETIME DEFAULT (datetime('now','localtime')),
	"active" BOOLEAN DEFAULT 1
);

/*
id            -- auto incrementing integer key
behaviour_id  -- link to the behaviour this session belongs to
name          -- name of the session
created_date  -- timestamp of when the session was created
active        -- is this session enabled or is it disabled, defaults to enabled 
*/
CREATE TABLE IF NOT EXISTS "Session" (
	"id" INTEGER PRIMARY KEY,
	"behaviour_id" INTEGER,
	"name" TEXT,
	"created_date" DATETIME DEFAULT (datetime('now','localtime')),
	"stopped" BOOLEAN DEFAULT 0,
	FOREIGN KEY ("behaviour_id") REFERENCES "Behaviour"("id") ON DELETE CASCADE
);




