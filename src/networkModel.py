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
import protocol
import canbus
import threading


class CFNode(object):
    """This class represents a CAN-FIX Node on the network"""
    def __init__(self, nodeID=None):
        self.nodeID = nodeID
        self.deviceID = 0x00
        self.model = 0x000000
        self.version = 0x00
        self.parameters = []
        self.configruation = []
        self.updated = time.time()

class NetworkModel(object):
    """This class represents a CAN-FIX network.  It contains
       network specific information, configuration and a list
       of all the current nodes seen on the network"""
    def __init__(self):
        self.nodes = []
    
    def __findNode(self, nodeid):
        """Find and return the node with the given ID"""
        for each in self.nodes:
            if each.nodeID == nodeID: return each
        return None

    def update(self, frame):
        p = protocol.parseFrame(frame)
        if isinstance(p, protocol.Parameter):
            print "Parameter:", p
        elif isinstance(p, protocol.NodeAlarm):
            print "Node Alarm:", p
        elif isinstance(p, protocol.NodeSpecific):
            print "Node Specific:", p
        elif isinstance(p, protocol.TwoWayMsg):
            print "2 Way Message:", p

