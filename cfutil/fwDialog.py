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

import sys
import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .ui.firmware_ui import Ui_dialogFirmware
from . import config
from . import devices
from . import firmware

log = logging.getLogger(__name__)

class FirmwareThread(QThread):
    progress = pyqtSignal("float")
    status = pyqtSignal(str)

    def __init__(self, fw):
        QThread.__init__(self)
        self.fw = fw
        self.fw.setStatusCallback(self.setStatus)
        self.fw.setProgressCallback(self.setProgress)
        self.fw.setStopCallback(self.setZeroProgress)

    def setStatus(self, status):
        self.status.emit(status)

    def setProgress(self, progress):
        self.progress.emit(progress * 100.0)

    def setZeroProgress(self):
        self.progress.emit(0.0)

    def run(self):
        try:
            self.fw.start_download()
        except firmware.FirmwareError as e:
            self.setStatus(str(e))
        except Exception as e:
            raise


class dialogFirmware(QDialog, Ui_dialogFirmware):
    def __init__(self, can, netmodel):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = QSettings()
        self.netmodel = netmodel
        self.can = can
        # Check config and set the file, node and device to last used
        try:
            self.editFile.setText(self.settings.value("firmware/filename"))
        except:
            pass
        #self.spinNode.setValue(self.settings.value("firmware/node", 1).toInt()[0])
        for each in self.netmodel.nodes:
            self.comboNode.addItem("[{}] {}".format(each.nodeID, each.name))
        self.labelStatus.setText("")

    def btnClick(self, btn):
        x = btn.text()
        if x == "&Apply":
            node = self.netmodel.nodes[self.comboNode.currentIndex()]
            driver = node.device.fwDriver
            #node = self.spinNode.value()
            self.settings.setValue("firmware/filename", self.editFile.text())
            #self.settings.setValue("firmware/node", node)
            #self.settings.setValue("firmware/driver", driver)
            try:
                self.fw = firmware.Firmware(driver, self.editFile.text())
            except IOError:
                qm = QMessageBox()
                qm.setText("Firmware File Not Found")
                qm.setWindowTitle("Error")
                qm.setIcon(QMessageBox.Warning)
                qm.exec_()
                return
            self.fw.srcNode = config.node
            self.fw.destNode = node.nodeID
            self.fw.device = node.device
            self.fw.can = self.can
            self.fwThread = FirmwareThread(self.fw)
            self.fwThread.status.connect(self.labelStatus.setText)
            self.fwThread.progress.connect(self.progressBar.setValue)
            self.fwThread.finished.connect(self.fwComplete)

            self.fwThread.start()
            btn.setText("Stop")
        if x == "&Stop":
            self.fw.stop()
            btn.setText("&Apply")
        if x == "&Close":
            self.fw.stop()

    def fwComplete(self):
        #self.labelStatus.setText("We Done")
        b = self.buttonBox.buttons()
        b[1].setText("&Apply")
        pass

    def btnFileClick(self):
        res = QFileDialog.getOpenFileName(self, 'Open File', '.')
        self.editFile.setText(res[0])
