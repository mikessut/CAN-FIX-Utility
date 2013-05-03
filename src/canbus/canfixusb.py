#  CAN-FIX Utilities - An Open Source CAN FIX Utility Package 
#  Copyright (c) 2013 Phil Birkelbach
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
import serial
import time
#from serial.tools.list_ports import comports

class Adapter():
    """Class that represents an the Open Source CAN-FIX-it USB to CANBus adapter"""
    def __init__(self):
        self.name = "CAN-FIX-it USB Adapter"
        self.shortname = "canfixusb"
        self.type = "serial"
        self.ser = None
        
    def __readResponse(self, ch):
        s = ""

        while 1:
            x = self.ser.read()
            if len(x) == 0:
                raise DeviceTimeout
            else:
                s = s + x
                if x == '\n':
                    if s[0] == ch.lower(): # Good Response
                        return s
                    if s[0] == "*": # Error
                        raise BusReadError("Error " + s[1] + " Returned")

    def connect(self, config):
        try:
            self.bitrate = config['bitrate']
        except KeyError:
            self.bitrate = 125
        bitrates = {125:"B125\n", 250:"B250\n", 500:"B500\n", 1000:"B1000\n"}
        try:
            self.portname = config['port']
        except KeyError:
            self.portname = comports[0][0]
        
        try:
            self.timeout = config['timeout']
        except KeyError:
            self.timeout = 0.25
            
        self.ser = serial.Serial(self.portname, 115200, timeout=self.timeout)
                
        print "Reseting CAN-FIX-it"
        print self.ser.write("K\n")
        try:
            result = self.__readResponse("K")
        except DeviceTimeout:
            raise BusInitError("Timeout waiting for adapter")
        except BusReadError:
            raise BusInitError("Unable to Reset adapter")
        
        print "Setting Bit Rate"
        self.ser.write(bitrates[self.bitrate])
        try:
            result = self.__readResponse("B")
        except DeviceTimeout:
            raise BusInitError("Timeout waiting for adapter")
        except BusReadError:
            raise BusInitError("Unable to set CAN Bit rate")
        self.open()
    
    def disconnect(self):
        self.close()

    def open(self):
        print "Opening CAN Port"
        self.ser.write("O\n")
        try:
            result = self.__readResponse("O")
        except DeviceTimeout:
            raise BusInitError("Timeout waiting for adapter")
        except BusReadError:
            raise BusInitError("Unable to Open CAN Port")

    def close(self):
        print "Closing CAN Port"
        self.ser.write("C\n")
        try:
            result = self.__readResponse("C")
        except DeviceTimeout:
            raise BusInitError("Timeout waiting for Adapter")
        except BusReadError:
            raise BusInitError("Unable to Close CAN Port")

    def error(self):
        self.ser.write("E\r")
        try:
            result = self.__readResponse("E")
        except DeviceTimeout:
            raise BusInitError("Timeout waiting for Adapter")
        except BusReadError:
            raise BusInitError("Unable to Close CAN Port")
        return int(result, 16)

    def sendFrame(self, frame):
        if frame['id'] < 0 or frame['id'] > 2047:
            raise ValueError("Frame ID out of range")
        xmit = "W"
        xmit = xmit + '%03X' % (frame['id'])
        #xmit = xmit + str(len(frame['data']))
        xmit = xmit + ':'
        for each in frame['data']:
            xmit = xmit + '%02X' % each
        xmit = xmit + '\n'
        self.ser.write(xmit)
        while True:
            try:
                result = self.__readResponse("W")
            except DeviceTimeout:
                raise BusWriteError("Timeout waiting for Adapter")
            if result[0] == 'w':
                continue
            elif result != 'z\r':
                print "result =", result
                raise BusWriteError("Bad response from Adapter")
            else:
                break


    def recvFrame(self):
        result = self.__readResponse("R")
        print result, 
        if result[0] != 'r':
            raise BusReadError("Unknown response from Adapter")
        frame = {}
        frame['id'] = int(result[1:4], 16)
        frame['data'] = []
        for n in range(int(result[5], 16)):
            frame['data'].append(int(result[5+n*2:7+n*2], 16))
        print frame
        return frame