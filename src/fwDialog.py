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
import protocol
import devices
import sys
import connection
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui.firmware_ui import Ui_dialogFirmware


class dialogFirmware(QDialog, Ui_dialogFirmware):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        #TODO: Check config and set the file, node and device to last used
        for each in devices.devices:
            self.comboDevice.addItem(each.name)
        
    def btnClick(self, btn):
        x = btn.text()
        if x == "Apply":
            self.labelStatus.setText("GO GO Now!!")
    
    def btnFileClick(self):
        filename = filename = QFileDialog.getOpenFileName(self, 'Open File', '.')
        self.editFile.setText(filename)
