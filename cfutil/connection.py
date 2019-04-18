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

log = logging.getLogger("root.connection")

_connections = []
_bus = None
_busLock = threading.Lock()
_recvThread = None

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
    def __init__(self):
        self.recvQueue = queue.Queue()

    def send(self, msg):
        sendMsg(msg)

    def recv(self, block = True, timeout = None):
        return self.recvQueue.get(block, timeout = timeout)


class RecvThread(threading.Thread):
    def __init__(self):
        super(RecvThread, self).__init__()
        self.getout = False

    def run(self):
        while self.getout == False:
            msg = _bus.recv(timeout = 1.0)
            if msg:
                #print(msg)
                for each in _connections:
                    each.recvQueue.put(msg)

    def stop(self):
        self.getout = True


def sendMsg(msg):
    global _busLock
    global _bus
    with _busLock:
        _bus.send(msg)

def initialize(interface, channel, **kwargs):
    global _bus
    global _recvThread
    _bus = can.interface.Bus(channel, bustype = interface, **kwargs)
    _recvThread = RecvThread()
    _recvThread.start()


def stop():
    _recvThread.stop()
    if _recvThread.is_alive():
        _recvThread.join(1.0)
    #if _recvThread.is_alive():
    #    raise plugin.PluginFail
    _bus.shutdown()
    _connections = []


def connect():
    conn = Connection()
    _connections.append(conn)
    return conn

def disconnect(conn):
    _connections.remove(conn)
