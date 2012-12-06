#!/usr/bin/env python

import sys
import connection
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import protocol
from ui.main_ui import Ui_MainWindow
from ui.connect_ui import Ui_ConnectDialog

con = None

class connectDialog(QDialog, Ui_ConnectDialog):
    def __init__(self):
        global con
        QDialog.__init__(self)
        self.setupUi(self)
        con = connection.Connection()
        ports = con.getPortList()
        for each in ports:
            self.comboPort.addItem(each)


class modelData(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.cf = protocol.CanFix("../data/canfix.xml")
        self.parlist = []
        for i in self.cf.parameters:
            self.parlist.append(self.cf.parameters[i])
        self.parlist.sort(lambda a,b:cmp(a["id"], b["id"]))
        self.cols = 3
        
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        y = index.row()
        x = index.column()
        if x == 0:
           Q = self.parlist[y]["name"]
        elif x == 1:
           Q = self.parlist[y]["units"]
        elif x == 2:
           Q = self.parlist[y]["multiplier"]
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
            else:
                return QVariant("")
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(self.parlist[col]["id"])
        return QVariant()
    
    def edit(self, index):
        print "Edit Data Row %d" % index.row()


class modelDevices(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.rows = 100
        self.cols = 10
        
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant((index.row()+1)*100 + index.column()+1)
    
    def rowCount(self, parent = QModelIndex()):
        return self.rows
    
    def columnCount(self, parent = QModelIndex()):
        return self.cols
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("Column")
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant("Row")
        return QVariant()
    
    def edit(self, index):
        print "Edit Device Row %d" % index.row()


class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.data = modelData()
        self.tableData.setModel(self.data)
        self.devices = modelDevices()
        self.viewNetwork.setModel(self.devices)
        
#  def buttonDispatch(self):
#    btn = QObject.sender(self)
#    name = btn.objectName()
#    if name == "connectButton":        
#      print "Connect Button Pressed"
#      if self.readThread.isRunning():
#        print "Thread Already Running"
#      else:
#        self.readThread.start()
#    elif name == "writeButton":        
#      print "Write Button Pressed"
#    else:
#      print "Which Button is that????"
    def connect(self):
        print "Connect..."
        connectDia = connectDialog()
        x = connectDia.exec_()
        if x:
            port = str(connectDia.listPort.currentItem().text())
            self.statusbar.showMessage("Connecting to %s" % port)
            val = con.connect(port)
            if val:
                self.statusbar.showMessage("Connected to %s at %d baud.  Version %s" % 
                                          (val["Port"], val["Baudrate"], val["Version"]))
            else:
                self.statusbar.showMessage("Failed to connect to %s" % port)
        else:
            print "Canceled"

    def deviceEdit(self, index):
        self.devices.edit(index)
    
    def dataEdit(self, index):
        self.data.edit(index)
  
  
if __name__ == "__main__":
  app = QApplication(sys.argv)
  myapp = mainWindow()
  myapp.show()
  sys.exit(app.exec_())
  