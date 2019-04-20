============
Development
============


CAN Bus Connection
-------------------

The ``cfutil.connection.canbus`` object will be instantiated when the
``cfutil.connection`` module is imported for the first time.

There are two ways to interact with the CAN bus.  The first is to request
a Connection from the canbus object.  The other is to connect
to the newMessageCallback callback funciton.  The Connection object that
is returned from the canbus object is essentially nothing more than a
queue that acts like our own CAN bus.  The send funciton simply sends a
message through the Bus if it is connected.

The second way to interact with the CAN bus is to define the
``canbus.newMessageCallback member`` of the ``canbus`` object.  There is only one
callback.  It takes one argument and that is the python-can message that was
received.

These two methods can be used together but care should be taken to remove the
message frome the recieve queue by calling the ``recv`` function of the
connection object to keep the queue from filling up. In the gui part of this
program the callback method is used and it is turned into a pyqt signal that can
be used in multiple parts of the program.
