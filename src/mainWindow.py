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
    
    def run(self):
        canbus.enableRecvQueue(0)
        self.getout = False
        
        while True:
            try:
                frame = canbus.recvFrame(0)
                s = "%03X:" % (frame.id)
                for each in frame.data:
                    s = s + "%02X" % (each)
                #emit the signals
                self.newFrame.emit(frame)
                self.newFrameString.emit(s)
            except canbus.exceptions.DeviceTimeout:
                pass
            finally:
                if self.getout:
                    break
            
    def quit(self):
        self.getout = True
        

class connectDialog(QDialog, Ui_ConnectDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        ports = canbus.getSerialPortList()
        for each in ports:
            self.comboPort.addItem(each)
        for each in canbus.adapters:
            self.comboAdapter.addItem(each.name)
            
    def adapterChange(self, x):
        if canbus.adapters[x].type == "serial":
            self.stackConfig.setCurrentIndex(0)
        elif canbus.adapters[x].type == "network":
            self.stackConfig.setCurrentIndex(1)
        else:
            self.stackConfig.setCurrentIndex(2)
        
        
class modelData(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        #self.cf = protocol.CanFix(config.DataPath + "canfix.xml")
        self.parlist = []
        for i in protocol.parameters:
            self.parlist.append(protocol.parameters[i])
        self.parlist.sort(lambda a,b:cmp(a.id, b.id))
        self.cols = 3
        
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        y = index.row()
        x = index.column()
        if x == 0:
           Q = self.parlist[y].name
        elif x == 1:
           Q = self.parlist[y].units
        elif x == 2:
           Q = self.parlist[y].multiplier
        else:
           Q = None
        return QVariant(Q)
    
    def rowCount(self, parent = QModelIndex()):
        return len(self.parlist)
    
    def columnCount(self, parent = QModelIndex()):
        return self.cols
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0:
                return QVariant("Name")
            elif col == 1: 
                return QVariant("Units")
            elif col == 2:
                return QVariant("Multiplier")
            else:
                return QVariant("")
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(self.parlist[col].id)
        return QVariant()
    
    def edit(self, index):
        print "Edit Data Row %d" % index.row()


class modelNetwork(QAbstractItemModel):
    def __init__(self, parent=None):
        super(modelNetwork, self).__init__(parent)
        self.parents=[]
        self.rootItem = "Hello"
        self.rows = 100
        self.cols = 1
        
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant((index.row()+1)*100 + index.column()+1)
    
    def rowCount(self, parent):
        return self.rows
    
    def columnCount(self, parent):
        return self.cols
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("Column")
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant("Row")
        return QVariant()
    
    def index(self, row, column, parent):
        if row < 0 or column < 0 or \
           row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, colum, childItem)
        else:
            return QModelIndex

        

class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.data = modelData()
        self.tableData.setModel(self.data)
        self.network = QStandardItemModel()
        self.textTraffic.setReadOnly(True)
        parentItem = self.network.invisibleRootItem()
        for i in range(10):
            item = QStandardItem("Node " + str(i))
            parentItem.appendRow(item)
            for each in range(3):
                child = QStandardItem("Parameter " + str(each))
                item.appendRow(child)
            #parentItem = item
        #self.network = modelNetwork()
        self.viewNetwork.setModel(self.network)
        self.commThread = CommThread()
        
        
    def connect(self):
        print "Connect..."
        connectDia = connectDialog()
        x = connectDia.exec_()
        if x:
            config = {}
            index = connectDia.comboAdapter.currentIndex()
            config['port'] = str(connectDia.comboPort.currentText())
            config['address'] = str(connectDia.editAddress.text())
            self.statusbar.showMessage("Connecting to %s" % canbus.adapters[index].name)
            val = canbus.connect(index, config)
            if val:
                self.commThread.start()
                self.statusbar.showMessage("Connected to %s" % 
                                          (canbus.adapters[index].name))
                self.actionConnect.setDisabled(True)
                self.actionDisconnect.setEnabled(True)
                return True
            else:
                self.statusbar.showMessage("Failed to connect to %s" % config['port'])
                return False
        else:
            print "Canceled"
            return False
    
    def disconnect(self):
        self.commThread.quit() 
        self.commThread.wait()
        canbus.disconnect()
        self.actionConnect.setEnabled(True)
        self.actionDisconnect.setDisabled(True)
    
    def loadFirmware(self):
        if not self.commThread.isRunning():
            qm = QMessageBox()
            qm.setText("Please connect to a CANBus Network before trying to download firmware")
            qm.setWindowTitle("Error")
            qm.setIcon(QMessageBox.Warning)
            qm.exec_()
            if not self.connect(): # Try to connect
                return
        diaFirmware = fwDialog.dialogFirmware()
        x = diaFirmware.exec_()
                        
    def dataEdit(self, index):
        self.data.edit(index)
    
    def networkClicked(self, index):
        print index.parent().data().toString() + " " + index.data().toString()
        
    def trafficStart(self):
        self.commThread.newFrameString.connect(self.textTraffic.appendPlainText)
    
    def trafficStop(self):
        self.commThread.newFrameString.disconnect(self.textTraffic.appendPlainText)

def getout():
    global mWindow
    
    mainWindow.disconnect(mWindow)

def run(args):
    global mWindow
    app = QApplication(sys.argv)
    app.setOrganizationName("PetraSoft")
    app.setApplicationName("CAN-FIX Utility")
    mWindow = mainWindow()
    app.aboutToQuit.connect(getout)
    mWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
