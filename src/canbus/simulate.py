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

from exceptions import *
import Queue
import random
import time
import struct

class Node():
    def __init__(self, name = None):
        self.name = name
        self.nodeID = 255
        self.deviceType = 0
        self.model = 0xAABBCC
        self.FWRevision = 1
        
    def setFunction(self, function):
        self.frameFunction = function
        
    def doFrame(self, frame):
        """Function that handles incoming frames for the node"""
        
    def getFrame(self):
        """Function that produces a frame for the node."""

# These are just functions that generate messages for each of the 
# nodes that we've created.

r_fuel_qty = 22.0
l_fuel_qty = 22.0
fuel_flow = 7.0

def __func_fuel():
    pass

cht = (357 - 32 ) * 5/9
egt = (1340 - 32) * 5/9
oil_press = 78
oil_temp = (180-32) * 5/9
rpm = 2400
man_press = 24

def __func_engine():
    pass

airspeed = 165
altitude = 8500
oat = 10

def __func_airdata():
    pass    
    
def configNodes():
    nodelist = []
    for each in range(3):
        node = Node()
        node.nodeID = each + 1
        node.deviceType = 0x60
        node.model = 0x001
        nodelist.append(node)
    
    
class Adapter():
    """Class that represents a CAN Bus simulation adapter"""
    def __init__(self):
        self.name = "CAN Device Simulator"
        self.shortname = "simulate"
        self.type = "None"
        self.__rQueue = Queue.Queue()
        random.seed()
        self.airspeed = 1234
        self.nodes = configNodes()
    
    def connect(self, config):
        print "Connecting to simulation adapter"
        self.open()    
    
    def disconnect(self):
        print "Disconnecting from simulation adapter"
        self.close()
        
    def open(self):
        print "Opening CAN Port"

    def close(self):
        print "Closing CAN Port"

    def error(self):
        print "Closing CAN Port"

    def sendFrame(self, frame):
        if frame['id'] < 0 or frame['id'] > 2047:
            raise ValueError("Frame ID out of range")

    def recvFrame(self):
        if not self.__rQueue.empty():
            return self.__rQueue.get(0.25)
        else:
            o = (int(time.time()*100) % 4) - 2
            x = random.randint(0,9)
            if x < 9:
                time.sleep(0.25)
                raise DeviceTimeout()
            else:
                x = struct.pack('<H', self.airspeed+o)
                frame = {}
                frame['id'] = 0x183 #Indicated Airspeed
                frame['data'] = [2, 0, 0, ord(x[0]), ord(x[1])]
                return frame
        