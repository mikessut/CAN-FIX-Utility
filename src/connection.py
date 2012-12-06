#!/usr/bin/env python

import sys
import serial
import serial.tools.list_ports

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