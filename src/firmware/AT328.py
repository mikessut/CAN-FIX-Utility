#!/usr/bin/python

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

from intelhex import IntelHex
import crc
import canbus
import time
from fwBase import FirmwareBase
import firmware

class Driver(FirmwareBase):
    def __init__(self, filename, can):
        FirmwareBase.__init__(self)
        self.__ih = IntelHex()
        self.__ih.loadhex(filename)
        self.can = can
        
        cs = crc.crc16()
        for each in range(self.__ih.minaddr(), self.__ih.maxaddr()+1):
            cs.addByte(self.__ih[each])
        self.__size = self.__ih.maxaddr()+1
        self.__checksum = cs.getResult()
        self.__progress = 0.0
        self.__blocksize = 128
        self.__blocks = self.__size / self.__blocksize + 1
        self.__currentblock = 0


    def __fillBuffer(self, ch, address, data):
        sframe = canbus.Frame(1760 + ch, [0x01, address & 0xFF, (address & 0xFF00) >> 8, 128])
        self.can.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.can.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime:
                    return False
        for n in range(self.__blocksize / 8):
            #print data[address + (8*n):address + (8*n) + 8]
            sframe.data = data[address + (8*n):address + (8*n) + 8]
            self.can.sendFrame(sframe)
            #time.sleep(0.3)
            # TODO Need to deal with the abort from the uC somewhere
        return True

    def __erasePage(self, ch, address):
        sframe = canbus.Frame(1760 + ch, [0x02, address & 0xFF, (address & 0xFF00) >> 8, 64])
        self.can.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.can.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def __writePage(self, ch, address):
        sframe = canbus.Frame(1760 + ch, [0x03, address & 0xFF, (address & 0xFF00) >> 8])
        self.can.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.can.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def __sendComplete(self, ch):
        sframe = canbus.Frame(1760 + ch, [0x05, self.__checksum & 0xFF, (self.__checksum & 0xFF00) >> 8, \
                            self.__size & 0xFF, (self.__size & 0xFF00) >> 8])
        self.can.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.can.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def download(self, node):
        data=[]
        channel = FirmwareBase.start_download(self, node)
        for n in range(self.__blocks * self.__blocksize):
            data.append(self.__ih[n])
        for block in range(self.__blocks):
            address = block * 128
            #print "Buffer Fill at %d" % (address)
            self.sendStatus("Writing Block %d of %d" % (block, self.__blocks))
            self.sendProgress(float(block) / float(self.__blocks))
            self.__currentblock = block
            while(self.__fillBuffer(channel, address, data)==False):
                if self.kill: raise firmware.FirmwareError("Canceled")
            
            # Erase Page
            #print "Erase Page Address =", address
            self.__erasePage(channel ,address)
            
            # Write Page
            #print "Write Page Address =", address
            self.__writePage(channel ,address)
            
        #self.__progress = 1.0
        #print "Download Complete Checksum", hex(self.__checksum), "Size", self.__size
        self.__sendComplete(channel)
        self.sendStatus("Download Complete Checksum 0x%X, Size %d" % (self.__checksum, self.__size))
        self.sendProgress(1.0)
        #FirmwareBase.end_download()