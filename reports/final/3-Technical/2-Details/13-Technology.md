### Technologies {#sec-3-2-13-1}

The Aria system is composed of many different technologies that each serve a task specific purpose.
This section outlines the details about the technologies chosen and the reasons for them being 
selected. This section is broken down into the different subsystems of the Aria system.

##### Exchange Server {-}

The exchange server is responsible for logging and sending messages throughout the Aria system.
It functions as the central communication point for all messages within the Aria system. This server
needs to support the main communication protocols that are required for interfacing with several 
different protocols, including UDP, UPnP, Z-Wave and others. To accommodate this requirement, Python
3 was selected as the primary language.

Python 3 offers support for most of the desired protocols for this system. It can directly
interface with C allowing for support of any external library implementations. As for the version
decision of Python, choosing version 3 over version 2 allows us to use many of the new features that
Python offers. It also means that we are not writing Python using a set of deprecated standards.

###### Database {-}

The central exchange server needs to record all events and messages that it receives. This
database will be accessed by the exchange server and could be integrated into the exchange process.
The database needs to have transaction management but does not need to be a sophisticated database
server. SQLite provides all of the required features for this operation and provides the system with
a relational data store. Using SQLite means that the system will need SQL to read and write data 
from the database.

###### Quality Control {-}

To maintain the desired level of quality in development, tooling is needed to validate the system.
Both static and dynamic techniques for quality control are being used to aid in the development of 
the smart home system. For static code analysis of the exchange hub, **pyflakes** is being used to
stop syntax errors. This tool reads a python file and reports if it conforms to a set of desired 
constraints.

To check the system's dynamic functionality, the system has sets of integrated unit tests.
Python comes with a built-in unit testing framework appropriately named **unittest**. This package
is being used to develop test stubs and test cases to validate the operations of the exchange.
To drive these tests, **nosetools** is being used. This tool automatically discovers test cases and
manages running the test cases in a contained environment. The two tools complement each other
and create the basis for the exchange unit testing structure.

###### Communication Libraries {-}

In order to interface with different communication protocols, the central exchange is required to
use a number of different third party libraries to communicate. These libraries provide direct
translation from the exchange's internal message structure to the target devices communication
protocol.

###### WeMo {-}

The first of the these communication libraries is used to interface to WeMo devices and is titled
**netdisco**. This library provides the exchange command with the ability to discover WeMo devices,
get device states, as well as send control commands.

##### HTTP Gateway {-}

The HTTP Gateway is responsible for serving static web content as well as enabling communication
from the web client to the exchange server. The gateway creates a thin wrapper around the internal
communication structure of the exchange server and serves it to the web client with a RESTful API. 
To perform these tasks a simple new web technology, **node.js**, was used. Node is a JavaScript 
interpreter that provides a massive set of server development tools and libraries.

One of the easiest to use node packages is a web server called **Express**. Express is dynamically
configured by coding to its interfaces, which enables rapid development of a web server. This
technology has been used for the HTTP gateway to simplify the development.

###### Deployment {-}

In order to compile the server into a single executable, **Webpack** is being used. Webpack bundles
all of a systems source code into a single file and adds a node.js 'shebang' (`#!/usr/local/env node`)
to the start. This process allows the simple JavaScript files to be turned into an executable
bundle. For the full details of the deployment process, refer to [Appendix I-2](#I-2).

###### Package Management {-}

With almost any node.js project there are dependencies. This project is no exception as it uses
several packages for runtime, deployment and testing. Fortunately, node.js comes with a default
package manager appropriately named **Node Package Manager** (NPM). NPM is the standard for all
node.js projects and is consistent across various operating systems.

###### Quality Control {-}

To ensure that the code for the hub gateway is adequate and dependable, multiple testing and
validation techniques are used. First, the gateway code goes through a static analysis tool
called **JSHint** that checks for syntax and lexical errors. This phase quickly indicates where
issues may lie in code before it is even tested.

Static testing is quick and often useful, but does not test the execution of the gateway. In
order to dynamically test this gateway, the **Mocha** unit testing framework was added. This
framework provides a behaviour driven development (BDD) testing language for creating unit tests
for the gateway.

##### Web Client {-}

The web client is the front end facing user interface that controls the Aria system. The client is
responsible for providing observability of the system as well as controllability of the hub and
various devices. The web client is intended to be consumed in a user's web browser and therefore
must use the language of the web, JavaScript.

###### Deployment {-}

Deploying code to different web browsers tends to be a bit tricky, as most browsers deviate on their
implementation of the JavaScript language. To ensure that the web client will operate on the lowest
common denominator of browsers, a translation layer was used when building the client. This
translation tool, called **Babel**, allows JavaScript to be written using the newest version of the
EMCAScript specification, `es6`. This allows the JavaScript to still function on browsers that only 
support the older version `es5`. It does this by transpiling all of the new JavaScript features into
the old version equivalent ones.

Once the web client has been converted into browser executable code, it is then bundled into a
single web app file using **Webpack**. This is the same tool that is used for the gateway to make
it executable. Here the intent is to obfuscate and minimize the size of the web application so
that it has a faster load time on client. The full details about the deployment of the web
client are outlined in [Appendix I-2](#I-2).

###### Quality Control {-}

Similarly to the gateway, the web client undergoes two phases of testing; static and dynamic. The
static phase is exactly the same as the gateway as it is analyzed by JSHint. The dynamic phase
slightly differs as the target platform is vastly different from the gateway. In order to
dynamically test the remote, a testing library called **Jasmine** was used to write unit tests.
This library is similar to Mocha in that it provides a BDD testing grammar for creating unit tests.
To run these tests, a test driver called **Karma** was used in conjunction with a daemonized
browser called **PhantomJS**. The Karma driver runs the Jasmine tests in the PhantomJS browser to
simulate running tests in an end user's browser.


