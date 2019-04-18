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

log = logging.getLogger("mainWindow")

class CommThread(QThread):
    """Thread to handle the communication for the UI"""
    # We emit two signals.  One with the raw frame ...
    newMessage = pyqtSignal(can.Message)
    # .. The other with a formatted string.
    newMessageString = pyqtSignal('QString')

    def __init__(self, conn):
        QThread.__init__(self)
        self.conn = conn

    def run(self):
        self.getout = False
        while True:
            try:
                msg = self.conn.recv()
                #emit the signals
                self.newMessage.emit(msg)
                self.newMessageString.emit(str(msg))
            except canbus.exceptions.DeviceTimeout:
                pass
            finally:
                if self.getout:
                    break

    def stop(self):
        self.getout = True

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
    sigNodeAdded = pyqtSignal(int, name="nodeAdded")
    sigNodeIdent = pyqtSignal(int, dict, name="nodeAdded")

    def __init__(self, args):
        QMainWindow.__init__(self)
        self.conn = None
        self.setupUi(self)
        self.network = networkModel.NetworkModel()

        self.data = tableModel.ModelData()
        self.sigParameterAdded.connect(self.data.parameterAdd)
        self.sigParameterChanged.connect(self.data.parameterChange)
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

        self.commThread = None
        if config.auto_connect:
            self.connect_auto()

    # Generic Connection Function
    def __connect(self):
        connection.initialize(str(self.interface), str(self.channel))
        self.conn = connection.connect()
        if self.conn:
            self.commThread = CommThread(self.conn)
            self.commThread.start()
            self.statusbar.showMessage("Connected to %s" %
                                        (self.interface))
            self.actionConnect.setDisabled(True)
            self.actionDisconnect.setEnabled(True)
            #self.commThread.newFrame.connect(self.updateFrame)
            self.commThread.newMessage.connect(self.network.update)
            #We give the network model access to the can connection
            self.network.conn = self.conn
            # The network model is generic (not PyQt) so these tie the callbacks to the signals
            self.network.setCallback("parameterAdded", self.sigParameterAdded.emit)
            self.network.setCallback("nodeIdent", self.sigNodeIdent.emit)
            self.network.setCallback("parameterChanged", self.sigParameterChanged.emit)
            self.network.setCallback("nodeAdded", self.sigNodeAdded.emit)
            return True
        else:
            self.statusbar.showMessage("Failed to connect to %s" % config.device)
            return False


    # Called on startup if we have --interface=xxx in args
    def connect_auto(self):
        self.interface = config.interface
        self.channel = config.channel
        self.bitrate = config.bitrate
        return self.__connect()

    # GUI connect function
    def connect(self):
        # TODO setup with existing configuration
        connectDia = connectDialog()
        x = connectDia.exec_()
        if x:
            #config = canbus.Config()
            index = connectDia.comboAdapter.currentIndex()
            self.interface = connection.valid_interfaces[index]
            self.channel = connectDia.comboChannel.currentText()
            self.bitrate = 125 #TODO Change this to actually work
            self.statusbar.showMessage("Connecting to {}".format(self.interface))
            #self.conn = connection.connect()
            #self.can.device = str(connectDia.comboPort.currentText())
            #self.can.ipaddress = str(connectDia.editAddress.text())
            #self.can.timeout = 0.25
            return self.__connect()
        else:
            return False

    def disconnect(self):
        if self.commThread:
            self.commThread.stop()
            self.commThread.wait()
        if self.conn:
            connection.disconnect(self.conn)
            self.conn = None
        self.commThread = None
        self.actionConnect.setEnabled(True)
        self.actionDisconnect.setDisabled(True)

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

    def dataEdit(self, index):
        self.data.edit(index)

    def networkClicked(self, index):
        #pass
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
        self.commThread.newMessage.connect(self.trafficFrame)
        self.buttonStart.setDisabled(True)
        self.buttonStop.setEnabled(True)

    def trafficStop(self):
        self.commThread.newMessage.disconnect(self.trafficFrame)
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
