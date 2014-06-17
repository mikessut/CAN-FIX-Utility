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
import canbus
import threading
import devices


class CFNode(object):
    """This class represents a CAN-FIX Node on the network"""
    def __init__(self, nodeID=None):
        self.nodeID = nodeID
        self.name = "Unknown"
        self.deviceID = 0x00
        self.model = 0x000000
        self.version = 0x00
        self.parameters = []
        self.configruation = []
        self.updated = time.time()
    
    def updateParameter(self, par):
        self.updated = time.time()
        for i,each in enumerate(self.parameters):
            if each == par:
                each = par
                return i # returning the index indicates change
        else:
            self.parameters.append(par) #Add new parameter
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
        self.can = None
        # Data Update Callback Functions
        self.parameterAdded = None   # function(canfix.Parameter)
        self.parameterChanged = None # function(canfix.Parameter)
        self.nodeAdded = None        # function(int) - Node ID
        self.nodeChanged = None      # function(int, int) - Old Node ID, New Node ID
        self.nodeIdent = None        # function(int, {}) - nodeid, {name, deviceid, model, version}
    
    def __findNode(self, nodeid):
        """Find and return the node with the given ID"""
        for each in self.nodes:
            if each.nodeID == nodeid: return each
        return None

    
    def __addNode(self, nodeid):
        node = CFNode(nodeid)
        self.nodes.append(node)
        if self.nodeAdded:
            self.nodeAdded(nodeid)
        p = canfix.NodeSpecific()
        p.controlCode = 0x00 # Node Id Command
        p.sendNode = self.can.srcNode
        p.destNode = nodeid
        f = p.getFrame()
        self.can.sendFrame(f)
        p.controlCode = 0x05 # Node Report Command
        f = p.getFrame()
        self.can.sendFrame(f)
        return node
    
    def update(self, frame):
        p = canfix.parseFrame(frame)
        if isinstance(p, canfix.Parameter):
            node = self.__findNode(p.node)
            if node == None: # Node not in list, add it
                node = self.__addNode(p.node)
            assert node
            result = node.updateParameter(p)
            if result != None:
                if self.parameterChanged:
                    self.parameterChanged(p)
            else:
                if self.parameterAdded:
                    self.parameterAdded(p)
        elif isinstance(p, canfix.NodeAlarm):
            pass
        elif isinstance(p, canfix.NodeSpecific):
            node = self.__findNode(p.sendNode)
            if node == None:
                node = self.__addNode(p.sendNode)
            assert node
            if p.controlCode == 0: # Node ID
                node.deviceID = p.data[1]
                node.version = p.data[2]
                node.model = p.data[3] | p.data[4]<<8 | p.data[5]<<16
                device = devices.findDevice(node.deviceID, node.model)
                if device:
                    node.name = device.name
                if self.nodeIdent:
                    self.nodeIdent(p.sendNode, {"name":node.name, "deviceid":node.deviceID, 
                                                "model":node.model, "version":node.version})
        elif isinstance(p, canfix.TwoWayMsg):
            pass
        
    def setCallback(self, name, func):
        if name.lower() == "parameteradded":
            self.parameterAdded = func
        elif name.lower() == "parameterchanged":
            self.parameterChanged = func
        elif name.lower() == "nodeadded":
            self.nodeAdded = func
        elif name.lower() == "nodechanged":
            self.nodeChanged = func
        elif name.lower() == "nodeident":
            self.nodeIdent = func
 

    def __str__(self):
        s = ""
        for each in self.nodes:
            s += str(each)
        return s
