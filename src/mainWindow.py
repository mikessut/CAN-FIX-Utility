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
import devices
import sys
import canbus
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import protocol
from ui.main_ui import Ui_MainWindow
from ui.connect_ui import Ui_ConnectDialog
import fwDialog
import networkModel
import treeModel
import tableModel


class CommThread(QThread):
    """Thread to handle the communication for the UI"""
    # We emit two signals.  One with the raw frame ...
    newFrame = pyqtSignal(canbus.Frame)
    # .. The other with a formatted string.
    newFrameString = pyqtSignal('QString')
    
    def __init__(self, can):
        QThread.__init__(self)
        self.can = can
        
    def run(self):
        self.getout = False
        while True:
            try:
                frame = self.can.recvFrame()
                #emit the signals
                self.newFrame.emit(frame)
                self.newFrameString.emit(str(frame))
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
        ports = canbus.getSerialPortList()
        for each in ports:
            self.comboPort.addItem(each)
        for each in canbus.adapterList:
            self.comboAdapter.addItem(each.name)
            
    def adapterChange(self, x):
        if canbus.adapterList[x].type == "serial":
            self.stackConfig.setCurrentIndex(0)
        elif canbus.adapterList[x].type == "network":
            self.stackConfig.setCurrentIndex(1)
        else:
            self.stackConfig.setCurrentIndex(2)        


class MainWindow(QMainWindow, Ui_MainWindow):
    # Signals
    sigParameterAdded = pyqtSignal(protocol.Parameter, name="parameterAdded")
    sigParameterChanged = pyqtSignal(protocol.Parameter, name="parameterChanged")
            
    def __init__(self, args):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.network = networkModel.NetworkModel()
        self.data = tableModel.ModelData()
        self.sigParameterAdded.connect(self.data.parameterAdd)
        self.sigParameterChanged.connect(self.data.parameterChange)
        self.tableData.setModel(self.data)
        header = self.tableData.horizontalHeader()
        header.setResizeMode(QHeaderView.ResizeToContents)
        
        self.netView = treeModel.NetworkTreeModel()
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
        if args.adapter:
            self.connect_auto(args)
        
    # Generic Connection Function
    def __connect(self):
        self.can.connect()
        if self.can:
            self.commThread = CommThread(self.can)
            self.commThread.start()
            self.statusbar.showMessage("Connected to %s" % 
                                        (self.can.adapter.name))
            self.actionConnect.setDisabled(True)
            self.actionDisconnect.setEnabled(True)
            #self.commThread.newFrame.connect(self.updateFrame)
            self.commThread.newFrame.connect(self.network.update)
            #We give the network model access to the can connection
            self.network.can = self.can
            self.network.setCallback("parameterAdded", self.parameterAdded)
            self.network.setCallback("parameterChanged", self.parameterChanged)
            return True
        else:
            self.statusbar.showMessage("Failed to connect to %s" % config.device)
            return False
    
    def parameterAdded(self, parameter):
        self.sigParameterAdded.emit(parameter)
    def parameterChanged(self, parameter):
        self.sigParameterChanged.emit(parameter)
        
    
    # Called on startup if we have --adapter=xxx in args
    def connect_auto(self, args):
        self.can = canbus.Connection(args.adapter)
        if args.bitrate:
            self.can.bitrate = args.bitrate
        if args.ip_address:
            self.can.ipadress = args.ip_address
        if args.serial_port:
            self.can.devcie = args.serial_port
        return self.__connect()
    
    # GUI connect function
    def connect(self):
        connectDia = connectDialog()
        x = connectDia.exec_()
        if x:
            config = canbus.Config()
            index = connectDia.comboAdapter.currentIndex()
            self.statusbar.showMessage("Connecting to %s" % canbus.adapterList[index].name)
            self.can = canbus.Connection(canbus.adapterList[index].shortname)
            self.can.device = str(connectDia.comboPort.currentText())
            self.can.ipaddress = str(connectDia.editAddress.text())
            self.can.bitrate = 125 #TODO Change this to actually work
            self.can.timeout = 0.25
            return self.__connect()
        else:
            return False
    
    def disconnect(self):
        if self.commThread:
            self.commThread.stop() 
            self.commThread.wait()
        self.can.disconnect()
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
        diaFirmware = fwDialog.dialogFirmware(self.can)
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
        
    def trafficFrame(self, frame):
        if self.checkRaw.isChecked():
            self.textTraffic.appendPlainText(str(frame))
        else:
            p = protocol.parseFrame(frame)
            self.textTraffic.appendPlainText(str(p))
    
    def dataEdit(self, index):
        self.data.edit(index)
    
    def networkClicked(self, index):
        print index.parent().data().toString() + " " + index.data().toString()
    
    def networkDblClicked(self, index):
        print "Edit *", index.data().toString()
    
    def networkExpanded(self, index):
        print "Expand ->", index.data().toString()
        
    def networkContextMenu(self, point):
        self.popMenu.exec_(self.viewNetwork.mapToGlobal(point))  
        
    def trafficStart(self):
        self.commThread.newFrame.connect(self.trafficFrame)
        self.buttonStart.setDisabled(True)
        self.buttonStop.setEnabled(True)

    def trafficStop(self):
        self.commThread.newFrame.disconnect(self.trafficFrame)
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
    print mWindow.network
    sys.exit(result)
    
if __name__ == "__main__":
    run()
