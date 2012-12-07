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

#import sys
import serial
import serial.tools.list_ports
import adapters



class Connection:
    """Represent a generic connection to a CANBus network"""
    def __init__(self):
        self.connectCallback = None
        self.portdef = {}
        
    def connect(self, portname):
        try:
            self.ser = serial.Serial(portname, 115200, timeout=1)
            self.ser.write('V\r')
            version = self.ser.read(5)
        except:
            return None
        if version:
            self.portdef["Version"] = version
            self.portdef["Port"] = self.ser.name
            self.portdef["Baudrate"] = self.ser.baudrate
            return self.portdef
        else:
            return None
        
    def disconnect(self):
       self.ser.close()
       self.portdef = {}
       
    def getPortList(self):
        """Return a list of available ports"""
        self.portList = serial.tools.list_ports.comports()
        list = []
        for each in self.portList:
           list.append(each[0])
        return list