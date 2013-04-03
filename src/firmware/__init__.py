#!/usr/bin/python

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

from intelhex import IntelHex
import crc
import canbus
import string
import time
import argparse
import devices

class FirmwareError(Exception):
    """Base class for exceptions in this module"""
    pass

class Channels():
    """A Class to keep up with free CANFIX Channels"""
    def __init__(self):
        self.channel = [0]*16

    def GetFreeChannel(self):
        for each in range(16):
            if self.channel[each] == 0:
                return each
        return -1

    def ClearAll(self):
        for each in range(16):
            self.channel[each] = 0

    def TestFrame(self, frame):
        FirstChannel = 1760

        if frame.id >= FirstChannel and frame.id < FirstChannel+32:
            c = (frame.id - FirstChannel)/2
            self.channel[c] = 1


#class Firmware():
    #"""A Class that represents the firmware logic."""
    #def __init__(self, driver, filename):
        ## Here we import and assign the right download driver object
        #if driver == "AT328":
            #import AT328
            #self.__driver = AT328.Driver(filename)
        #elif driver == "DUMMY":
            #import DUMMY
            #self.__driver = DUMMY.Driver(filename)
        #else:
            #raise FirmwareError("No such device")
        #self.__kill = False
        #canbus.enableRecvQueue(2)

def Firmware(driver, filename):
    if driver == "AT328":
        import AT328
        return AT328.Driver(filename)
    elif driver == "DUMMY":
        import DUMMY
        return DUMMY.Driver(filename)
    else:
        raise FirmwareError("No such device")

def config():
    parser = argparse.ArgumentParser(description='CANFIX Firmware Downloader 1.0')
    parser.add_argument('--filename', '-f', nargs=1, help='Intel Hex File to Download', required=True)
    parser.add_argument('--port', '-p', nargs=1, help='Serial Port to find CANBus interface')
    parser.add_argument('--node', '-n', type=int, nargs=1, help='CAN-FIX Node number of device')
    args = parser.parse_args()
    args = vars(args)
    output = {}
    if args['port'] != None:
        output["portname"]= args['port'][0]
    else:
        output["portname"] = ""

    output["filename"] = args['filename'][0]
    output["node"] = args['node'][0]

    return output


#***** MAIN ROUTINE *****
def main():
    exit()
       
if __name__ == '__main__':
    main()