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

import argparse

Have_PyQt = True
try:
    from PyQt4.QtGui import *
except ImportError:
    Have_PyQt = False

parser = argparse.ArgumentParser(description='CAN-FIX Configuration Utility Program')
parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')

args = parser.parse_args()

if Have_PyQt==False or args.interactive == True:
    import mainCommand
    mainCommand.run()
else:
    import mainWindow
    mainWindow.run()
    