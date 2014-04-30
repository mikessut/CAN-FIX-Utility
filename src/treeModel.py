#!/usr/bin/env python

#  CAN-FIX Utilities - An Open Source CAN FIX Utility Package 
#  Copyright (c) 2014 Phil Birkelbach
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import protocol
import canbus

#Nodes in the network tree.  Not to be confused with CAN-FIX Nodes
class TreeItem(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children= []
        self.value = None
    
    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row]
    
    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1
    
    def __len__(self):
        return len(self.children)
    
    def __str__(self):
        return self.name

class FixItem(TreeItem):
    """Represents an actual CAN-FIX Network Node"""
    def __init__(self, name, nodeID, parent=None):
        super(FixItem, self).__init__(name, parent)
        self.nodeID = nodeID
        n = TreeItem("Node ID", self)
        n.value = nodeID
        self.children.append(n)
        self.children.append(TreeItem("Device", self))
        self.children.append(TreeItem("Model", self))
        self.children.append(TreeItem("Version", self))
        self.children.append(TreeItem("Parameters", self))
        self.children.append(TreeItem("Configuration", self))
        self.updated = time.time()
    
    def getDeviceItem(self):
        return self.children[1]
    deviceItem = property(getDeviceItem)
    def getModelItem(self):
        return self.children[2]
    modelItem = property(getModelItem)
    def getVersionItem(self):
        return self.children[3]
    versionItem = property(getVersionItem)
    def getParameterItem(self):
        return self.children[4]
    parameterItem = property(getParameterItem)
    
    def __cmp__(self, other):
        if self.nodeID < other.nodeID:
            return -1
        elif self.nodeID > other.nodeID:
            return 1
        else:
            return 0

class ParameterItem(TreeItem):
    """Represents a CAN-FIX Parameter"""
    def __init__(self, name, pid, parent=None):
        super(ParameterItem, self).__init__(name, parent)
        self.identifier = pid
        self.index = 0
        self.indexName = None
    
    def __str__(self):
        if self.indexName:
            return "%s %s %i" % (self.name, self.indexName, self.index +1)
        else:
            return self.name
    
    def __cmp__(self, other):
        if self.identifier < other.identifier:
            return -1
        elif self.identifier > other.identifier:
            return 1
        else:
            if self.indexName:
                if self.index < other.index:
                    return -1
                elif self.index > other.index:
                    return 1
            return 0
    

# Debug print routine.
def TreePrint(node, depth=0):
    for i in range(depth):
        print "",
    #print node, "<-", node.parent
    print node, node.value
    if node.children:
        for each in node.children:
            TreePrint(each, depth+1)    

class NetworkTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkTreeModel, self).__init__(parent)
        self.parents=[]
        self.root = TreeItem("root")
        self.rows = 0
        self.cols = 2
        self.can = None
        
     # The following functions are here for interface to the view.
    
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)
        assert node is not None
        if index.column()==0:
            return QVariant(str(node))
        elif index.column()==1:
            return QVariant(node.value)
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and col == 0:
            return QVariant("CAN-FIX Network")
        return QVariant()

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column, branch.childAtRow(row))
    
    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        return len(node)
    
    def columnCount(self, parent):
        return self.cols
    
    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)
    
    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root
        
    # These functions are for controlling the information in the model    
    # Most of these are called as slots from the main networkModel
    def findNodeID(self, nodeid):
        """returns the FixItem that has the matching node id"""
        for each in self.root.children:
            if each.nodeID == nodeid:
                return each
        return None
    
    def nodeAdd(self, nodeid):
        n = FixItem("Unknown", nodeid, self.root)
        self.root.children.append(n)
        self.modelReset.emit()
    
    def nodeIdent(self, nodeid, info):
        item = self.findNodeID(nodeid)
        item.name = info['name']
        item.deviceItem.value = info['deviceid']
        item.modelItem.value = info['model']
        item.versionItem.value = info['version']
        #self.dataChanged.emit(self.createIndex(0,0,p), self.createIndex(1,1,p))
        
    def parameterAdd(self, parameter):
        item = self.findNodeID(parameter.node)
        p = item.parameterItem
        newp = ParameterItem(parameter.name, parameter.identifier, p)
        newp.value = parameter.valueStr()
        if parameter.indexName:
            newp.indexName = parameter.indexName
            newp.index = parameter.index
        p.children.append(newp)
        #self.dataChanged.emit(self.createIndex(0,0,p), self.createIndex(1,1,p))
                
    def parameterChange(self, parameter):
        item = self.findNodeID(parameter.node)
        p = item.parameterItem
        for i, each in enumerate(p.children):
            if each == parameter:
                each.value = parameter.valueStr(units=True)
                self.dataChanged.emit(self.createIndex(i,1,each), self.createIndex(i,1,each))

