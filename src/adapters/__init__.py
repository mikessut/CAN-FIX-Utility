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


# This module is to abstract the interface between the code and the
# CANBus communication adapters.  Right now it only works with the
# EasySync USB2-F-7xxx devices.  The idea is to create classes for
# each type of device that we want to use and have a common interface
# for each.  While connecting we'd figure out what kind of device that
# we have and then set pointers to the right device classes so the rest
# of the program doesn't have to worry about what device it is using

class BusError(Exception):
    """Base class for exceptions in this module"""
    pass

class BusInitError(BusError):
    """CAN Bus Initialization Error"""
    def __init__(self, msg):
        self.msg = msg

class BusReadError(BusError):
    """CAN Bus Read Error"""
    def __init__(self, msg):
        self.msg = msg

class BusWriteError(BusError):
    """CAN Bus Write Error"""
    def __init__(self, msg):
        self.msg = msg

class DeviceTimeout(Exception):
    """Device Timeout Exception"""
    pass

import easy
import simulate
import network

adapters = []
adapters.append(easy.Adapter())
adapters.append(simulate.Adapter())
adapters.append(network.Adapter())

