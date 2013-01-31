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

class Driver(object):
    def __init__(self, filename):
        self.__ih = IntelHex()
        self.__ih.loadhex(filename)
            
        cs = crc.crc16()
        for each in range(self.__ih.minaddr(), self.__ih.maxaddr()+1):
            cs.addByte(self.__ih[each])
        self.__size = self.__ih.maxaddr()+1
        self.__checksum = cs.getResult()
        self.__progress = 0.0
        self.__blocksize = 128
        self.__blocks = self.__size / self.__blocksize + 1
        self.__currentblock = 0

    def statusCallback(self, status):
        """Called to set a callback function that this object
           will use to send a status string to the caller"""
        self.__statusCallback = status
    
    def progressCallback(self, progress):
        """CAlled to set a callback function that this object
           will use to send the progress to the caller.  The
           progress is a floating point numnber between 0.0 and 1.0"""
        self.__progressCallback = progress

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
        
    def __fillBuffer(ch, address, data):
        sframe = canbus.Frame(1760 + ch, [0x01, address & 0xFF, (address & 0xFF00) >> 8, 128])
        canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False
        for n in range(self.__blocksize / 8):
            #print data[address + (8*n):address + (8*n) + 8]
            sendProgress(float(address + 8*n) / float(self.size))
            sframe.data = data[address + (8*n):address + (8*n) + 8]
            canbus.sendFrame(sframe)
            #time.sleep(0.3)
            # TODO Need to deal with the abort from the uC somewhere

    def __erasePage(self, ch, address):
        sframe = canbus.Frame(1760 + ch, [0x02, address & 0xFF, (address & 0xFF00) >> 8, 64])
        canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def __writePage(self, ch, address):
        sframe = canbus.Frame(1760 + ch, [0x03, address & 0xFF, (address & 0xFF00) >> 8])
        canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def __sendComplete(self, ch):
        sframe = canbus.Frame(1760 + ch, [0x05, __checksum & 0xFF, (__checksum & 0xFF00) >> 8, \
                            __size & 0xFF, (__size & 0xFF00) >> 8])
        canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe.id == sframe.id+1 and \
                    rframe.data == sframe.data: break
                now = time.time()
                if now > endtime: return False

    def download(self, ch, node):
        for n in range(self.__blocks * self.__blocksize):
            data.append(self.__ih[n])
        for block in range(self.__blocks):
            address = block * 128
            print "Buffer Fill at %d" % (address)
            sendStatus("Writing Block %d of %d" % block, self.blocks)
            self.__currentblock = block
            self.__fillBuffer(channel, address, data)
            # TODO Deal with timeout of above
            
            # Erase Page
            print "Erase Page Address =", address
            self.__erasePage(channel ,address)
            
            # Write Page
            print "Write Page Address =", address
            self.__writePage(channel ,address)
            
        self.__progress = 1.0
        print "Download Complete Checksum", hex(self.__checksum), "Size", self.__size
        self.__sendComplete(channel)
        sendStatus("Download Complete Checksum 0x%X, Size %d" % (hex(self.__checksum), self.__size))
        