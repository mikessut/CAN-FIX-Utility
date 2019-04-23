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

import time
import canfix
import collections
from cfutil import connection

canbus = connection.canbus

class FirmwareError(Exception):
    pass

class FirmwareBase:
    """Base Class for all firmware download drivers"""
    def __init__(self):
        # kill when set to True should stop downloads
        self.kill = False
        self.can = None

        # This is our node number
        self.srcNode = None
        self.destNode = None
        self.device = None # Object from EDS file
        self.__statusCallback = None
        self.__progressCallback = None
        self.__stopCallback = None

    def setProgressCallback(self, progress):
        if isinstance(progress, collections.Callable):
            self.__progressCallback = progress
        else:
            raise TypeError("Argument passed is not a function")

    def setStatusCallback(self, status):
        if isinstance(status, collections.Callable):
            self.__statusCallback = status
        else:
            raise TypeError("Argument passed is not a function")

    def setStopCallback(self, stop):
        if isinstance(stop, collections.Callable):
            self.__stopCallback = stop
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
        if self.__stopCallback:
            self.__stopCallback()

    # Download support functions
    def __getFreeChannel(self):
        """Waits for a half a second to see if there is any traffic on any
           of the channels and returns the channel number of the first
           free channel"""
        endtime = time.time() + 0.5
        self.channels = [0]*16
        while True: # Channel wait loop
            try:
                rframe = self.can.recv(0.1)
                msg = canfix.parseMessage(rframe)
                if isinstance(msg, canfix.TwoWayConnection):
                    self.channels[msg.channel] = 1
            except connection.Timeout:
                pass
            finally:
                now = time.time()
                if now > endtime: break
        for ch, v in enumerate(self.channels):
            if v == 0: return ch

    def __tryFirmwareReq(self):
        """Requests a firmware load, waits for 1/2 a second and determines
           if the response is correct and if so returns True returns
           False on timeout"""
        channel = self.__getFreeChannel()
        msg = canfix.UpdateFirmware(node=self.destNode, verification=self.device.fwUpdateCode, channel=channel)
        msg.sendNode = self.srcNode
        msg.msgType = canfix.MSG_REQUEST
        print(msg)
        self.can.send(msg.msg)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            if self.kill: raise FirmwareError("Canceled")
            try:
                rframe = self.can.recv(0.1)
            except connection.Timeout:
                pass
            else:
                msg = canfix.parseMessage(rframe)
                if isinstance(msg, canfix.UpdateFirmware):
                    if msg.destNode == self.node:
                        if msg.status == canfix.MSG_SUCCESS:
                            return True
                        else:
                            raise FirmewareError("Error {} Received".format(msg.errorCode))
            finally:
                now = time.time()
                if now > endtime: return False
        return True

    def start_download(self):
        """this function is called from the derived class object to find
           a free channel and send the firmware request messages."""
        attempt = 0
        while True: # Firmware load request loop
            if self.kill: raise FirmwareError("Canceled")
            self.sendStatus("Download Attempt " + str(attempt))
            attempt += 1
            if self.__tryFirmwareReq(): break
        print("Okay so we're going to give 'er a go")
