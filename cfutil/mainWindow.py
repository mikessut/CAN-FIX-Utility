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
import os
import can
import logging
import canfix
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from . import config
from . import devices
from . import connection
from .ui.main_ui import Ui_MainWindow
from .ui.connect_ui import Ui_ConnectDialog
from . import fwDialog
from . import networkModel
from . import treeModel
from . import tableModel

log = logging.getLogger(__name__)
canbus = connection.canbus

class connectDialog(QDialog, Ui_ConnectDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        for each in connection.valid_interfaces:
            self.comboAdapter.addItem(each)


    def interfaceChange(self, x):
        interface = connection.valid_interfaces[x]
        self.comboChannel.clear()
        for each in connection.get_available_channels(interface):
            self.comboChannel.addItem(each)
        if interface in ['serial', 'usb2can']:
            self.groupBitrate.setEnabled(True)
        else:
            self.groupBitrate.setEnabled(False)


class MainWindow(QMainWindow, Ui_MainWindow):
    # Signals
    sigParameterAdded = pyqtSignal(canfix.Parameter, name="parameterAdded")
    sigParameterChanged = pyqtSignal(canfix.Parameter, name="parameterChanged")
    sigParameterDeleted = pyqtSignal(canfix.Parameter, name="parameterDelted")
    sigNodeAdded = pyqtSignal(int, name="nodeAdded")
    sigNodeIdent = pyqtSignal(int, dict, name="nodeAdded")
    recvMessage = pyqtSignal(can.Message)
    sendMessage = pyqtSignal(can.Message)
    canbusConnected = pyqtSignal()
    canbusDisconnected = pyqtSignal()


    def __init__(self, args):
        QMainWindow.__init__(self)
        self.conn = None
        self.setupUi(self)
        self.network = networkModel.NetworkModel()

        self.data = tableModel.ModelData()
        self.sigParameterAdded.connect(self.data.parameterAdd)
        self.sigParameterChanged.connect(self.data.parameterChange)
        self.sigParameterDeleted.connect(self.data.parameterDelete)
        self.tableData.setModel(self.data)
        header = self.tableData.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.netView = treeModel.NetworkTreeModel()
        self.sigNodeAdded.connect(self.netView.nodeAdd)
        self.sigNodeIdent.connect(self.netView.nodeIdent)
        self.sigParameterAdded.connect(self.netView.parameterAdd)
        self.sigParameterChanged.connect(self.netView.parameterChange)
        self.viewNetwork.setModel(self.netView)
        self.viewNetwork.setContextMenuPolicy(Qt.CustomContextMenu)

        self.textTraffic.setReadOnly(True)

        actionStatus = QAction('Status', self)
        actionConfigure = QAction('Configure', self)
        actionEnable = QAction('Enable', self)
        actionDisable = QAction('Disable', self)
        actionFirmware = QAction('Firmware', self)

        self.popMenu = QMenu(self)
        self.popMenu.addAction(actionConfigure)
        self.popMenu.addAction(actionEnable)
        self.popMenu.addAction(actionDisable)
        self.popMenu.addSeparator()
        self.popMenu.addAction(actionStatus)

        # Take the callbacks from the canbus object and turn them into signals
        canbus.recvMessageCallback = self.recvMessage.emit
        canbus.sendMessageCallback = self.sendMessage.emit
        canbus.connectedCallback = self.canbusConnected.emit
        canbus.disconnectedCallback = self.canbusDisconnected.emit
        # ...Then connect them to stuff
        self.recvMessage.connect(self.network.update)

        # The network model is generic (not PyQt) so these tie the callbacks to the signals
        self.network.parameterAdded = self.sigParameterAdded.emit
        self.network.parameterChanged = self.sigParameterChanged.emit
        self.network.parameterDeleted = self.sigParameterDeleted.emit
        self.network.nodeIdent = self.sigNodeIdent.emit
        self.network.nodeAdded = self.sigNodeAdded.emit

        self.canbusConnected.connect(self.connectedSlot)
        self.canbusDisconnected.connect(self.disconnectedSlot)

        if canbus.connected:
            self.connectedSlot()
        else:
            self.disconnectedSlot()

    # Generic Connection Function
    def __connect(self):
        if canbus.connected:
            log.error("Already connected to {}".format(canbus.interface))
            return False
        try:
            canbus.connect(str(self.interface), str(self.channel))
            #self.commThread.newFrame.connect(self.updateFrame)
            return True
        except:
            self.statusbar.showMessage("Failed to connect to {}:{}".format(self.interface, self.channel))
            return False

    # GUI connect function
    def connect(self):
        # TODO setup with existing configuration
        connectDia = connectDialog()
        x = connectDia.exec_()
        if x:
            index = connectDia.comboAdapter.currentIndex()
            self.interface = connection.valid_interfaces[index]
            self.channel = connectDia.comboChannel.currentText()
            self.bitrate = 125 #TODO Change this to actually work
            return self.__connect()
        else:
            return False

    def disconnect(self):
        canbus.disconnect()


    def loadFirmware(self):
        if not self.commThread or not self.commThread.isRunning():
            qm = QMessageBox()
            qm.setText("Please connect to a CANBus Network before trying to download firmware")
            qm.setWindowTitle("Error")
            qm.setIcon(QMessageBox.Warning)
            qm.exec_()
            if not self.connect(): # Try to connect
                return
        self.commThread.stop()
        diaFirmware = fwDialog.dialogFirmware(self.can, self.network)
        x = diaFirmware.exec_()
        self.commThread.start()

    def updateFrame(self, frame):
        tab = self.tabWidget.currentIndex()
        if tab == 0: #Network Tree View
            self.netView.update(frame)
            self.viewNetwork.resizeColumnToContents(0)
        elif tab == 1: #Data Table View
            self.data.update(frame)
        elif tab == 3: #PFD
            #PFD Update
            pass

    def trafficFrame(self, msg):
        if self.checkRaw.isChecked():
            self.textTraffic.appendPlainText(str(msg))
        else:
            p = canfix.parseMessage(msg)
            self.textTraffic.appendPlainText(str(p))


    def connectedSlot(self):
        self.actionConnect.setDisabled(True)
        self.actionDisconnect.setEnabled(True)
        self.statusbar.showMessage("Connected to {}:{}".format(canbus.interface, canbus.channel))


    def disconnectedSlot(self):
        self.actionConnect.setEnabled(True)
        self.actionDisconnect.setDisabled(True)
        self.statusbar.showMessage("Disconnected")

    def dataEdit(self, index):
        self.data.edit(index)

    def networkClicked(self, index):
        #log.debug(index.parent().data().toString() + " " + index.data().toString())
        log.debug(index.parent().data() + " " + index.data())

    def networkDblClicked(self, index):
        item = index.internalPointer()
        if isinstance(item, treeModel.FixItem):
            print("Edit Node", item.nodeID)
        else:
            print(type(item))
        #print "Edit *", index.data().toString()

    def networkExpanded(self, index):
        #print "Expand ->", index.data().toString()
        self.viewNetwork.resizeColumnToContents(0)

    def networkCollapsed(self, index):
        #print "Collapse <-", index.data().toString()
        self.viewNetwork.resizeColumnToContents(0)

    def networkContextMenu(self, point):
        self.popMenu.exec_(self.viewNetwork.mapToGlobal(point))

    def trafficStart(self):
        self.recvMessage.connect(self.trafficFrame)
        self.sendMessage.connect(self.trafficFrame)
        self.buttonStart.setDisabled(True)
        self.buttonStop.setEnabled(True)

    def trafficStop(self):
        self.recvMessage.disconnect(self.trafficFrame)
        self.sendMessage.disconnect(self.trafficFrame)
        self.buttonStop.setDisabled(True)
        self.buttonStart.setEnabled(True)


def getout():
    global mWindow

    MainWindow.disconnect(mWindow)

def run(args):
    global mWindow
    app = QApplication(sys.argv)
    app.setOrganizationName("PetraSoft")
    app.setApplicationName("CAN-FIX Utility")
    mWindow = MainWindow(args)
    app.aboutToQuit.connect(getout)
    mWindow.show()
    result = app.exec_()
    # DEBUG Only
    #print(mWindow.network)
    os._exit(result)

if __name__ == "__main__":
    run()
