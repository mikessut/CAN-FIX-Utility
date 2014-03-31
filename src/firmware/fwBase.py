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

import canbus
import time
import firmware

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


class FirmwareBase:
    """Base Class for all firmware download drivers"""
    def __init__(self):
        # .kill when set to True should stop downloads
        self.kill = False
        
    def setProgressCallback(self, progress):
        if callable(progress):
            self.__progressCallback = progress
        else:
            raise TypeError("Argument passed is not a function")
        
    def setStatusCallback(self, status):
        if callable(status):
            self.__statusCallback = status
        else:
            raise TypeError("Argument passed is not a function")
        
    def sendStatus(self, status):
        """Function used by this object to test that the callback
            has been set and if so call it"""
        if self.__statusCallback:
            self.__statusCallback(status)
        
    def sendProgress(self, progress):
        """Function used by this object to test that the callback
           has been set and if so call it"""
        if self.__progressCallback:
            self.__progressCallback(progress)
            
    def stop(self):
        self.kill = True
        
    # Download support functions
    def __tryChannel(self, ch):
        """Waits for a half a second to see if there is any traffic on any
           of the channels"""
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            try:
                rframe = self.can.recvFrame(canbusQueue)
                ch.TestFrame(rframe)
            except canbus.DeviceTimeout:
                pass
            finally:
                now = time.time()
                if now > endtime: break

    def __tryFirmwareReq(self, ch, node):
        """Requests a firmware load, waits for 1/2 a second and determines
           if the response is correct and if so returns True returns
           False on timeout"""
        channel = ch.GetFreeChannel()
        sframe = canbus.Frame(1792 + canbus.srcNode, [node, 7, 1, 0xF7, channel])
        self.can.sendFrame(sframe)
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            if self.kill: raise firmware.FirmwareError("Canceled")
            try:
                rframe = self.can.recvFrame(canbusQueue)
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == (1792 + node) and \
                   rframe.data[0] == self.__srcnode: break
            finally:
                now = time.time()
                if now > endtime: return False
        return True

    def start_download(self, node):
        """this function is called from the derived class object to find
           a free channel and send the firmware request messages."""
        ch = Channels()
        data = []
        attempt = 0
        while True: # Firmware load request loop
            if self.kill: raise firmware.FirmwareError("Canceled")
            self.sendStatus("Trying Channel " + str(attempt))
            attempt += 1
            self.__tryChannel(ch)
            # send firmware request
            if self.__tryFirmwareReq(ch, node): break
        # Here we are in the Firmware load mode of the node    
        # Get our firmware bytes into a normal list
        return ch.GetFreeChannel()
  