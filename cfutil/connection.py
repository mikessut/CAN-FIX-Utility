#!/usr/bin/env python

#  CAN-FIX Utilities - An Open Source CAN FIX Utility Package
#  Copyright (c) 2012 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# This module represents a generic CAN Bus connection.  One CAN connection
# is made on the backend and it is shared among all parts of the program
# that need a 'dedicated' connection.  Similar to the loopback in socketcan

import threading
import logging
import can
try:
    import queue
except:
    import Queue as queue
import cfutil.config as config

log = logging.getLogger(__name__)

valid_interfaces = sorted(can.interfaces.VALID_INTERFACES)
log.debug("valid interfaces = {}".format(valid_interfaces))

def get_available_channels(interface):
    if interface == "serial":
        return config.portlist
    elif "socketcan" in interface:
        return config.config.get("can", "socketcan_channels").split(',')
    elif interface == "kvaser":
        return config.config.get("can", "kvaser_channels").split(',')
    elif interface == "pcan":
        return config.config.get("can", "pcan_channels").split(',')
    else:
        return []


class Connection:
    """Represent a generic connection to a CANBus network"""
    def __init__(self, sendFunction=None):
        self.recvQueue = queue.Queue()
        self.__sendFunction = sendFunction

    def send(self, msg):
        self.__sendFunction(msg)

    def recv(self, block = True, timeout = None):
        return self.recvQueue.get(block, timeout = timeout)


class CANBus(threading.Thread):
    def __init__(self):
        super(CANBus, self).__init__()
        self.getout = False
        self.daemon = True
        self.__connections = []
        self.__bus = None
        self.__connected = threading.Event()
        self.__connectedCallback = None
        self.__disconnectedCallback = None
        self.__newMessageCallback = None


    def run(self):
        while self.getout == False:
            connect_flag = self.__connected.wait(1.0)
            if connect_flag:
                msg = self.__bus.recv(timeout = 1.0)
                if msg:
                    #print(msg)
                    for each in self.__connections:
                        each.recvQueue.put(msg)
                    if self.__newMessageCallback != None:
                        self.__newMessageCallback(msg)

    def send(self, msg):
        self.__bus.send(msg)

    def connect(self, channel, interface, **kwargs):
        try:
            self.__bus = can.ThreadSafeBus(channel, bustype = interface, **kwargs)
        except Exception as e:
            log.error(e)
        if self.__connectCallback is not None:
            self.__connectCallback()
        self.__connected.set()

    def disconnect(self):
        self.__bus.shutdown()
        if self.__disconnectCallback is not None:
            self.__connectCallback()
        self.__disconnected.clear()

    def get_connected(self):
        return self.__connected.isSet()
    connected = property(get_connected)

    def connect_wait(self, timeout=None):
        return self.__connected.wait(timeout)

    def get_connection(self):
        c = Connection(self.send)
        self.__connections.append(c)
        return c

    def free_connection(self, c):
        self.__connections.remove(c)

    def stop(self):
        self.getout = True

canbus = CANBus()
canbus.start()
