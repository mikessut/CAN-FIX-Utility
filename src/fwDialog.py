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
#import connection
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui.firmware_ui import Ui_dialogFirmware
import firmware

class FirmwareThread(QThread):
    progress = pyqtSignal("float")
    status = pyqtSignal(QString)
    
    def __init__(self, fw, node):
        QThread.__init__(self)
        self.fw = fw
        self.node = node
        self.fw.setStatusCallback(self.setStatus)
        self.fw.setProgressCallback(self.setProgress)
    
    def setStatus(self, status):
        self.status.emit(status)
        
    def setProgress(self, progress):
        self.progress.emit(progress * 100.0)
        
    def run(self):
        self.fw.download(self.node)
        self.progress.emit(100.0)
        #self.status.emit("Finished")


class dialogFirmware(QDialog, Ui_dialogFirmware):
    def __init__(self, can):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = QSettings()
        self.editFile.setText(self.settings.value("firmware/filename").toString())
        self.spinNode.setValue(self.settings.value("firmware/node", 1).toInt()[0])
        #TODO: Check config and set the file, node and device to last used
        for each in devices.devices:
            self.comboDevice.addItem(each.name)
        self.can = can
        
    def btnClick(self, btn):
        x = btn.text()
        if x == "Apply":
            driver = devices.devices[self.comboDevice.currentIndex()].fwDriver
            node = self.spinNode.value()
            self.settings.setValue("firmware/filename", self.editFile.text())
            self.settings.setValue("firmware/node", node)
            self.settings.setValue("firmware/driver", driver)
            try:
                self.fw = firmware.Firmware(driver, self.editFile.text(), self.can)
            except IOError:
                qm = QMessageBox()
                qm.setText("Firmware File Not Found")
                qm.setWindowTitle("Error")
                qm.setIcon(QMessageBox.Warning)
                qm.exec_()
                return
            self.fwThread = FirmwareThread(self.fw, node)
            self.fwThread.status.connect(self.labelStatus.setText)
            self.fwThread.progress.connect(self.progressBar.setValue)
            self.fwThread.finished.connect(self.fwComplete)
            
            self.fwThread.start()
        if x == "Close":
            self.fw.stop()
                    
    def fwComplete(self):
        #self.labelStatus.setText("We Done")
        pass
        
    def btnFileClick(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', '.')
        self.editFile.setText(filename)
