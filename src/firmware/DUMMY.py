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

class DUMMY_Driver(object):
    def __init__(self, filename):
        self.__ih = IntelHex()
        self.__ih.loadhex(filename)
        
        cs = crc.crc16()
        for each in range(self.__ih.minaddr(), self.__ih.maxaddr()+1):
            cs.addByte(self.__ih[each])
        self.__size = self.__ih.maxaddr()+1
        self.__checksum = cs.getResult()

    def statusCallback(self, status):
        self.__statusCallback = status
    
    def progressCallback(self, progress):
        self.__progressCallback = progress

    def sendStatus(self, status):
        if self.__statusCallback:
            self.__statusCallback(status)
    
    def sendProgress(self, progress):
        if self.__progressCallback:
            self.__progressCallback(progress)

    def download():
        pass