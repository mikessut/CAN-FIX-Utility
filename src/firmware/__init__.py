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

class Firmware():
    """A Class that represents the firmware logic."""
    def __init__(self, driver, filename):
        # Here we import and assign the right download driver object
        if driver == "AT328":
            import AT328
            self.__driver = AT328.Driver(filename)
        elif driver == "DUMMY":
            import DUMMY
            self.__driver = DUMMY.Driver(filename)
        else:
            raise FirmwareError("No such device")
        self.__kill = False
        
    # Download support functions
    def __tryChannel(self, ch):
        """Waits for a half a second to see if there is any traffic on any
           of the channels"""
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                ch.TestFrame(rframe)
                now = time.time()
                if now > endtime: break

    def __tryFirmwareReq(self, ch, node):
        """Requests a firmware load, waits for 1/2 a second and determines
           if the response is correct and if so returns True returns
           False on timeout"""
        channel = ch.GetFreeChannel()
        sframe = canbus.frame(1792 + canbus.srcnode, node, 7, 1, 0xF7, channel)
        canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == (1792 + node) and \
                   rframe.data[0] == self.__srcnode: break
                now = time.time()
                if now > endtime: return False
        return True

    def setProgressCallback(self, progress):
        if callable(progress):
            self.__driver.progressCallback = progress
        else:
            raise TypeError("Argument passed is not a function")
        
    def setStatusCallback(self, status):
        if callable(status):
            self.__driver.statusCallback = status
        else:
            raise TypeError("Argument passed is not a function")
        
    
    def download(self, node):
        ch = Channels()
        data = []
        while True: # Firmware load request loop
            print "Trying Channel"
            self.__tryChannel(ch)
            # send firmware request
            if self.__tryFirmwareReq(ch, node): break
            if self.kill: exit(-1)
        # Here we are in the Firmware load mode of the node    
        # Get our firmware bytes into a normal list
        channel = ch.GetFreeChannel()
            
    def getProgress(self):
        return self.__progress
    
    def getCurrentBlock(self):
        return self.__currentblock
    
    def getBlocks(self):
        return self.__blocks
        
    def getSize(self):
        return self.__size
        
    def getChecksum(self):
        return self.__checksum
        
    currentblock = property(getCurrentBlock)
    progress = property(getProgress)
    blocks = property(getBlocks)
    size = property(getSize)
    checksum = property(getChecksum)
        
        
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