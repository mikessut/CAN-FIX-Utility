#!/usr/bin/env python

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

import config
import argparse
import canbus

Have_PyQt = True
try:
    from PyQt4.QtGui import *
except ImportError:
    Have_PyQt = False

parser = argparse.ArgumentParser(description='CAN-FIX Configuration Utility Program')
parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
l=[]
for each in canbus.adapterList:
    l.append(each.shortname)
parser.add_argument('--adapter', choices=l, help='CANBus Connection Adapter Name')
parser.add_argument('--bitrate', default=125, type=int, help='CANBus Bitrate')
parser.add_argument('--serial-port', help='CANBus Adapter Serial Port Device Name')
parser.add_argument('--ip-address', help='CANBus Network Adapter IP Address')
parser.add_argument('--firmware-file', help='Firmware filename')
parser.add_argument('--firmware-node', help='Node number to use in firmware download')
parser.add_argument('--device', help='CANFIX Device Name')
parser.add_argument('--device-id', help='CANFIX Device Identifier')
parser.add_argument('--list-devices', action='store_true', help='List all known devices and their device IDs')
parser.add_argument('--listen', action='store_true', help='Listen on the CANBus network and print to STDOUT')
parser.add_argument('--frame-count', type=int, default=0, help='Number of frames to print before exiting')

args = parser.parse_args()

if Have_PyQt==False or args.interactive == True:
    import mainCommand
    mainCommand.run(args)
else:
    import mainWindow
    mainWindow.run(args)
    