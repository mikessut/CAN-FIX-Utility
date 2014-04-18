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
    

# Debug print routine.
def TreePrint(node, depth=0):
    for i in range(depth):
        print "",
    #print node, "<-", node.parent
    print node, node.value
    if node.children:
        for each in node.children:
            TreePrint(each, depth+1)    

class NetworkModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkModel, self).__init__(parent)
        self.parents=[]
        self.root = TreeItem("root")
        self.rows = 0
        self.cols = 2
        self.can = None
        
        n = FixItem("Dummy", 1, self.root)
        pp = n.parameterItem   
        p = ParameterItem("Engine Power", 1310, pp)
        p.value = "75"
        pp.children.append(p)
        p = ParameterItem("Total Engine Time", 1312, pp)
        p.value = "250"
        pp.children.append(p)
        self.root.children.append(n)
        
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
    
    def findNodeID(self, nodeid):
        for each in self.root.children:
            if each.nodeID == nodeid:
                return each
        return None
    
    def updateParameter(self, item, parameter):
        p = item.parameterItem
        for i, each in enumerate(p.children):
            if each.identifier == parameter.identifier:
                each.value = parameter.valueStr(units=True)
                print "Update %s %i" % (each, i)
                self.dataChanged.emit(self.createIndex(i,1,each), self.createIndex(i,1,each))
                return
        newp = ParameterItem(parameter.name, parameter.identifier, p)
        p.children.append(newp)
    
    def update(self, frame):
        p = protocol.parseFrame(frame)
        if isinstance(p, protocol.Parameter):
            item = self.findNodeID(p.node)
            if item:
                self.updateParameter(item, p)
            else:
                n = FixItem("Unknown", p.node, self.root)
                self.root.children.append(n)
                self.updateParameter(n, p)
                self.modelReset.emit()
        else:
            print "Not a parameter"
        
