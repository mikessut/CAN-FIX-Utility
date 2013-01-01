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

class Adapter():
    """Class that represents a CAN Bus simulation adapter"""
    def __init__(self):
        self.name = "CAN Device Simulator"
        self.shortname = "simulate"
        self.type = "None"
        self.__rQueue = Queue.Queue()
        random.seed()
        self.airspeed = 1000
    
    def connect(self, config):
        print "Connecting to simulation adapter"

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
            x = random.randint(0,9)
            if x < 9:
                time.sleep(0.25)
                raise DeviceTimeout()
            else:
                frame = {}
                frame['id'] = 0x183 #Indicated Airspeed
                frame['data'] = [2, 0, 0, self.airspeed % 8, (self.airspeed / 256 )%8]
                return frame
        