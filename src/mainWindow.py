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

class LiveParameter(object):
    def __init__(self, name, units, value):
        self.name = name
        self.units = units
        self.setValue(value)
        
    def setValue(self, value):
        self.value = value
        #self.update = time.time()

class LiveParameterList(object):
    def __init__(self):
        self.list = []
        
    def update(self, frame):
        p = protocol.parseFrame(frame)
        if isinstance(p, protocol.Parameter):
            for each in self.list:
                if each.name == p.name:
                    each.setValue(p.value)
                    return len(self.list) 
            newparam = LiveParameter(p.name, p.units, p.value)
            self.list.append(newparam)
            return 0
            
    def getItem(self, row, column):
        if column == 0:
            return self.list[row].name
        elif column == 1:
            return self.list[row].value
        elif column == 2:
            return self.list[row].units
    
    def rowCount(self):
        return len(self.list)

class ModelData(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.parlist = LiveParameterList()
        
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        item = self.parlist.getItem(index.row(), index.column())
        return QVariant(item)
    
    def rowCount(self, parent = QModelIndex()):
        return self.parlist.rowCount()
    
    def columnCount(self, parent = QModelIndex()):
        return 3
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0:
                return QVariant("Name")
            elif col == 1: 
                return QVariant("Value")
            elif col == 2:
                return QVariant("Units")
            else:
                return QVariant("")
        #if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #    return QVariant(self.parlist[col].id)
        return QVariant()
    
    def edit(self, index):
        print "Edit Data Row %d" % index.row()

    def update(self, frame):
        if self.parlist.update(frame):
            self.dataChanged.emit(self.index(0,0),self.index(self.rowCount(), 3))
        else:
            self.modelReset.emit()

class ModelNetwork(QAbstractItemModel):
    def __init__(self, parent=None):
        super(ModelNetwork, self).__init__(parent)
        self.parents=[]
        self.rootItem = QStandardItem()
        self.rows = 10
        self.cols = 1
        self.node = ["Device Type", "Model", "Parameters"]
        
    def data(self, index, role):
        print "data()", index.row(), index.parent()
        if role == Qt.TextAlignmentRole:
            return QVariant(int(At.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        if index.parent()==self.rootItem:
            return QVariant((index.row()+1)*100 + index.column()+1)
        else:
            return QVariant(self.node[index.row()])
        
    def rowCount(self, parent):
        if not parent.isValid():
            print "rowCount() Invalid Parent"
            return self.rows
        if parent == self.rootItem:
            print "rowCount() Parent = root"
            return 2
        return 0
    
    def columnCount(self, parent):
        return self.cols
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("CAN-FIX Network")
        return QVariant()
    
    def index(self, row, column, parent):
        print "index() called", row, column
        if row < 0 or column < 0 or \
           row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()
        if not parent.isValid():
            print "not parent.isValid()"
            return self.createIndex(row, column, self.rootItem)
        print "Make a child?"
        childItem = parentItem.child(row)
        if childItem:
            print "return a child"
            return self.createIndex(row, colum, childItem)
        else:
            return QModelIndex()
    
    #def parent(self, child):

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.data = ModelData()
        self.tableData.setModel(self.data)
        
        self.network = QStandardItemModel()
        #self.network = ModelNetwork()
        parentItem = self.network.invisibleRootItem()
        for i in range(10):
            item = QStandardItem("Node " + str(i))
            parentItem.appendRow(item)
            for each in range(3):
                child = QStandardItem("Parameter " + str(each))
                item.appendRow(child)
        self.viewNetwork.setModel(self.network)
        self.textTraffic.setReadOnly(True)
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
            #TODO Need to make this come and go with tab focus
            self.commThread.newFrame.connect(self.data.update)
            return True
        else:
            self.statusbar.showMessage("Failed to connect to %s" % config.device)
            return False
    
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
        print "Connect..."
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
            print "Canceled"
            return False
    
    def disconnect(self):
        print "Disconnect() Called"
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
        
    def trafficStart(self):
        #self.commThread.newFrameString.connect(self.textTraffic.appendPlainText)
        self.commThread.newFrame.connect(self.trafficFrame)
        self.buttonStart.setDisabled(True)
        self.buttonStop.setEnabled(True)

    def trafficStop(self):
        #self.commThread.newFrameString.disconnect(self.textTraffic.appendPlainText)
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
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
