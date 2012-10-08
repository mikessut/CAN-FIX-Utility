#!/usr/bin/python

import serial
from serial.tools.list_ports import comports
import time

# This module is to abstract the interface between the code and the
# CANBus communication devices.  Right now it only works with the
# EasySync USB2-F-7xxx devcies.  The idea is to create classes for
# each type of device that we want to use and have a common interface
# for each.  While connecting we'd figure out what kind of device that
# we have and then set pointers to the right device classes so the rest
# of the program doesn't have to worry about what device it is using

class Connection():
    """Class that represents a connection to a CAN device"""

    def readResponse(self):
        str = ""

        while 1:
            x = self.ser.read()
            if len(x) == 0:
                return -1
            else:
                str = str + x
                if x == "\r": # Good Response
                    return str
                if x == "\x07": # Bell is error
                    return x

    def Easy_Init(self):
        bitrates = {10:"S0\r", 20:"S1\r", 50:"S2\r", 100:"S3\r", 
                    125:"S4\r", 250:"S5\r", 500:"S6\r", 800:"S7\r", 1000:"S8\r"}
        print "Reseting USB2-F-7x01"
        self.ser.write("R\r")
        result = self.readResponse()
        if result != "\r":
            print "Unable to Reset USB2-F-7x01"
            exit(-1)
        time.sleep(2)

        print "Setting Bit Rate"
        self.ser.write(bitrates[self.bitrate])
        result = self.readResponse()
        if result != "\r":
            print "Unable to set CAN Bit rate"
            exit(-1)

    def Easy_Open(self):
        print "Opening CAN Port"
        self.ser.write("O\r")
        result = self.readResponse()
        if result != "\r":
            print "Unable to Open CAN Port"
            exit(-1) #TODO: Raise an exception instead
        

    def __init__(self, portname = "", bitrate = 125):
        self.portname = portname
        self.bitrate = bitrate

    def connect(self):
        #This code tries to find a USB/CAN device on one of the comm ports.
        if self.portname == "":
            for each in comports():
                if string.find(each[1], "USB2-F-7x01") >= 0:
                    self.portname = each[0]
                    print "Found CAN device on Port", self.portname

        if self.portname == "":
            print "No CAN device found"
            print comports()
            exit(-1) #TODO: Raise an exception instead

        self.ser = serial.Serial(self.portname, 115200, timeout=0.5)
        self.init = self.Easy_Init
        self.openport = self.Easy_Open




if __name__ == '__main__':
    can = Connection("/dev/ttyUSB0")
    can.connect()
    can.init()
    can.openport()