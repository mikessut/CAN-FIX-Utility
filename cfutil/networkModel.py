#!/usr/bin/env python

#  CAN-FIX Utilities - An Open Source CAN FIX Utility Package
#  Copyright (c) 2014 Phil Birkelbach
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

#  This module handles the primary model of the CAN-FIX network
#  All of the information about the status and configuration of
#  the currently connected network will be kept here and then
#  distributed to the parts of the program that need it.

import time
import canfix
import can
import threading
import logging
from . import devices
from . import config
from . import connection
log = logging.getLogger("networkModel")

canbus = connection.canbus


class ConfigItem(object):
    def __init__(self, c):
        """c is the individual config dictionary from the device file"""
        self.__value = None
        self.__dict = c
        self.changeFunction = None

    def getKey(self):
        return self.__dict['key']
    key = property(getKey)

    def getName(self):
        return self.__dict['name']
    name = property(getName)

    def getDataType(self):
        return self.__dict['type']
    datatype = property(getDataType)

    def getUnits(self):
        return self.__dict.get('units', '')
    units = property(getUnits)

    def getMultiplier(self):
        return self.__dict.get('multiplier', 1.0)
    multiplier = property(getMultiplier)

    def setValue(self, value):
        if value != self.__value:
            self.__value = value;
            if self.changeFunction is not None:
                self.changeFunction(value)

    def getValue(self):
        return self.__value

    value = property(getValue, setValue)

    # Retrives a copy of the dictionary along with the value
    def getDict(self):
        d = self.__dict.copy()
        d['value'] = self.value
        return d
    dict = property(getDict)

    # Make us look like a dictionary
    def get(self, key, default=None):
        return self.__dict.get(key, default)

    def __str__(self):
        return "{} {} {} {} {}*{}".format(self.key, self.name, self.datatype, self.value, self.units, self.multiplier)


class CFNode(object):
    """This class represents a CAN-FIX Node on the network"""
    def __init__(self, nodeID=None):
        self.nodeID = nodeID
        self.name = "Unknown"
        self.deviceID = 0x00
        self.model = 0x000000
        self.version = 0x00
        self.device = None
        self.parameters = []
        self.configuration = []
        self.stale = False # Flag to help indicate
        self.updated = time.time()

    def update(self):
        self.updated = time.time()
        self.stale = False

    def updateParameter(self, par):
        self.update()
        for i,each in enumerate(self.parameters):
            if each == par:
                self.parameters[i] = par
                return i # returning the index indicates change
        self.parameters.append(par) #Add new parameter
        #self.parameters.sort()
        return None

    def __str__(self):
        s = "%s 0x%02X\n" % (self.name, self.nodeID)
        s += "  Device ID %i\n" % (self.deviceID, )
        s += "  Model Number %X\n" % self.model
        s += "  Version %X\n" % self.version
        s += "  Parameters"
        for each in self.parameters:
            s += "\n    %s" % each
        s += "\n  Last Update " + str(time.time()-self.updated) + "\n"
        return s


class NetworkModel(object):
    """This class represents a CAN-FIX network.  It contains
       network specific information, configuration and a list
       of all the current nodes seen on the network"""
    def __init__(self):
        self.nodes = []
        self.conn = None
        # Data Update Callback Functions
        self.parameterAdded = None   # function(canfix.Parameter)
        self.parameterChanged = None # function(canfix.Parameter)
        self.parameterDeleted = None # function(canfix.Parameter)
        self.nodeAdded = None        # function(int) - Node ID
        self.nodeChanged = None      # function(int, int) - Old Node ID, New Node ID
        self.nodeDeleted = None      # function(int) - Node ID
        self.nodeIdent = None        # function(int, {}) - nodeid, {name, deviceid, model, version}
        self.configAdded = None      # function(int, {}) - nodeid, {key, name, type, units, value}
        self.configChanged = None    # function(int, {}) - nodeid, {key, name, type, units, value}
        self.configDeleted = None    # function(int, int) - nodeid, key
        self.maintTimer = TimerThread(2.0, self.maintenance)
        self.maintTimer.start()

    def __findNode(self, nodeid, create=True):
        """Find and return the node with the given ID"""
        for each in self.nodes:
            if each.nodeID == nodeid: return each
        if create:
            return self.__addNode(nodeid)
        return None

    def __deleteNode(self, node):
        if self.parameterDeleted is not None:
            for p in node.parameters:
                self.parameterDeleted(p)
        if self.nodeDeleted is not None:
            self.nodeDeleted(node.nodeID)
        self.nodes.remove(node)

    def __addNode(self, nodeid):
        node = CFNode(nodeid)
        self.nodes.append(node)
        if self.nodeAdded is not None:
            self.nodeAdded(nodeid)
        p = canfix.NodeIdentification()
        p.sendNode = int(config.node)
        p.destNode = nodeid
        m = p.getMessage()
        canbus.send(m)

        p = canfix.NodeReport()
        p.sendNode = int(config.node)
        p.destNode = nodeid
        m = p.getMessage()
        canbus.send(m)
        return node

    def update(self, msg):
        p = canfix.parseMessage(msg)
        node = None
        if isinstance(p, canfix.Parameter):
            node = self.__findNode(p.node)
            assert node
            result = node.updateParameter(p)
            if result != None:
                if self.parameterChanged is not None:
                    self.parameterChanged(p)
            else:
                if self.parameterAdded is not None:
                    self.parameterAdded(p)
        elif isinstance(p, canfix.NodeAlarm):
            pass
        elif isinstance(p, canfix.NodeStatus):
            node = p.sendNode
        elif isinstance(p, canfix.NodeIdentification):
            node = self.__findNode(p.sendNode)
            assert node
            node.deviceID = p.device
            node.version = p.fwrev
            node.model = p.model
            device = devices.findDevice(node.deviceID, node.model, node.version)
            if device:
                node.name = device.name
                node.device = device
            if self.nodeIdent:
                self.nodeIdent(p.sendNode, {"name":node.name, "deviceid":node.deviceID,
                                            "model":node.model, "version":node.version})
        elif isinstance(p, canfix.TwoWayMsg):
            pass

        if node is not None:
            node.update()

    # We assign this function to our config objuects so they can have proper
    # access to our callback function
    def configChangeLink(self, nodeID, cfg):
        def f(value):
            if self.configChanged is not None:
                self.configChanged(nodeID, cfg.getDict())
            can = canbus.get_connection()
            msg = canfix.NodeConfigurationSet(key=cfg.get("key"), datatype=cfg.get("type"), multiplier=cfg.get("multiplier"))
            msg.sendNode = config.node
            msg.destNode = nodeID
            msg.value = value
            can.send(msg.msg)
            start = time.time()
            while(True):
                try:
                    res = can.recv(timeout=1.0)
                except connection.Timeout:
                    res = None #None = timeout
                    break
                if res.arbitration_id == 1760 + nodeID and res.data[0] == 0x09 and res.data[1] == config.node:
                    break # We've found our response
                elif time.time() - start > 1.0:
                    res = None # None = timeout
                    break
            if res is None:
                log.error("Timeout while waiting for configuration data")
            else:
                msg.msg = res

                if msg.errorCode:
                    log.error("Error reading configuration for {}".format(cfg.get('name')))
                    cfg.value = "$error$"
                else:
                    cfg.value = value
            canbus.free_connection(can)
        return f


    def readConfiguration(self, node):
        can = canbus.get_connection()
        for c in node.device.configuration:
            #print(c)
            multiplier = c.get("multiplier", 1.0)
            msg = canfix.NodeConfigurationQuery(key=c["key"], datatype=c["type"], multiplier=multiplier)
            msg.sendNode = config.node
            msg.destNode = node.nodeID
            #print(msg.msg)
            can.send(msg.msg)
            start = time.time()
            while(True):
                try:
                    res = can.recv(timeout=1.0)
                except connection.Timeout:
                    res = None #None = timeout
                    break
                if res.arbitration_id == 1760 + node.nodeID and res.data[0] == 0x0A and res.data[1] == config.node:
                    break # We've found our response
                elif time.time() - start > 1.0:
                    res = None # None = timeout
                    break
            if res is None:
                log.error("Timeout while waiting for configuration data")
            else:
                msg.msg = res
                msg.datatype = c['type']
                cfi = ConfigItem(c)
                # cfi.key = c['key']
                # cfi.name = c['name']
                # cfi.datatype = c['type']
                # cfi.units = c.get('units', None)
                if msg.error:
                    log.error("Error reading configuration for {}".format(c['name']))
                    cfi.value = "$error$"
                else:
                    cfi.value = msg.value
                cfi.changeFunction = self.configChangeLink(node.nodeID, cfi)
                node.configuration.append(cfi)
                if self.configAdded is not None:
                    self.configAdded(node.nodeID, cfi.dict)
        canbus.free_connection(can)


    def __str__(self):
        s = ""
        for each in self.nodes:
            s += str(each)
        return s


    def maintenance(self):
        for node in self.nodes:
            if node.stale:
                self.__deleteNode(node)
            else:
                if time.time() - node.updated > 2.0:
                    node.stale = True
                    p = canfix.NodeIdentification()
                    p.sendNode = int(config.node)
                    p.destNode = node.nodeID
                    m = p.getMessage()
                    canbus.send(m)

                    p = canfix.NodeReport()
                    p.sendNode = int(config.node)
                    p.destNode = node.nodeID
                    m = p.getMessage()
                    canbus.send(m)
            if node.device is not None and node.configuration == []:
                self.readConfiguration(node)

# Kinda like the built in threading.Timer except this one is recurring and
# is a daemon thread so it'll die with the rest of the application
class TimerThread(threading.Thread):
    def __init__(self, interval, function):
        super(TimerThread, self).__init__()
        self.daemon = True
        self.interval = interval
        self.function = function

    def run(self):
        while True:
            time.sleep(self.interval)
            self.function()
