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

# This file represents the dialog box that is used to save the configuration
# of a particular node to a file.

import sys
import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .ui.configSave_ui import Ui_ConfigSaveDialog
#from . import config
from . import devices
#from . import firmware

log = logging.getLogger(__name__)




class dialogConfigSave(QDialog, Ui_ConfigSaveDialog):
    def __init__(self, netmodel, nodeid=0, boxtype="SAVE"):
        QDialog.__init__(self)
        self.setupUi(self)
        self.netmodel = netmodel
        #self.nodeid = nodeid
        # self.device = None
        # self.model = None
        # self.version = None
        # So hitting enter doesn't send the value or close the box
        self.saveButton = self.buttonBox.button(QDialogButtonBox.Save)
        self.saveButton.setEnabled(False)
        self.cancelButton = self.buttonBox.button(QDialogButtonBox.Cancel)
        self.closeButton = self.buttonBox.button(QDialogButtonBox.Close)

        #Btn.setAutoDefault(False)
        #Btn.setDefault(False)
        self.cancelButton.hide()

        self.nodeChange(nodeid)
        self.spinBoxNode.setValue(nodeid)

        self.labelStatus.hide()
        self.progressBar.hide()

        if boxtype == "SAVE":
            self.setWindowTitle("Save Node Configuration")
        else:
            self.setWindowTitle("Load Node Configuration")

        # self.widget = getConfigItemWidget(self.configItem, self.scrollAreaWidgetContents)
        # self.formLayout.setWidget(0, QFormLayout.LabelRole, self.widget)
        # if c.units is not None:
        #     l = QLabel(self.scrollAreaWidgetContents)
        #     l.setText(c.units)
        #     self.formLayout.setWidget(0, QFormLayout.FieldRole, l)

    # This function looks through the network model and if it can find
    # a node it populates the dialog with the proper information
    def nodeChange(self, nodeid):
        found = None
        for node in self.netmodel.nodes:
            if node.nodeID == nodeid:
                found = node
                break
        if found is None:
            self.node = None
            self.labelNodeName.setText("Unknown Device")
            self.labelDevice.setText("Unknown")
            self.labelModel.setText("Unknown")
            self.labelVersion.setText("Unknown")
            self.spinBoxStart.setValue(0)
            self.spinBoxLast.setValue(0)
        else:
            self.node = found
            self.labelNodeName.setText(self.node.name)
            self.labelDevice.setText(str(self.node.deviceID))
            self.labelModel.setText(str(self.node.model))
            self.labelVersion.setText(str(self.node.version))
            if self.node.configuration:
                min = max = self.node.configuration[0].key
                for c in self.node.configuration:
                    if c.key < min: min = c.key
                    if c.key > max: max = c.key
            else:
                min = 0
                max = 0
            self.spinBoxStart.setValue(min)
            self.spinBoxLast.setValue(max)


    def btnClick(self, btn):
        if btn == self.buttonBox.button(QDialogButtonBox.Save):
            self.cancelButton.show()
            self.closeButton.hide()
        if btn == self.buttonBox.button(QDialogButtonBox.Cancel):
            self.cancelButton.hide()
            self.closeButton.show()
        if btn == self.buttonBox.button(QDialogButtonBox.Close):
            self.close()


    def btnFileClick(self):
        fd = QFileDialog()
        fd.setNameFilter("Json Files (*.json)")
        fd.setFileMode(QFileDialog.AnyFile)
        if self.lineEditFileName.text():
            fd.selectFile(self.lineEditFileName.text())
        else:
            fd.selectFile("device{}.json".format(self.labelDevice.text()))
        if fd.exec():
            filenames = fd.selectedFiles()
            self.lineEditFileName.setText(filenames[0])


    def closeEvent(self, e):
        e.accept()
