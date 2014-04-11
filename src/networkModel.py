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

#Nodes in the network tree.  Not to be confused with CAN-FIX Nodes
class TreeNode(object):
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

# Debug print routine.
def NodePrint(node, depth=0):
    for i in range(depth):
        print "",
    print node, "<-", node.parent
    if node.children:
        for each in node.children:
            NodePrint(each, depth+1)    

class NetworkModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(NetworkModel, self).__init__(parent)
        self.parents=[]
        self.root = TreeNode("root")
        self.rows = 0
        self.cols = 2
        
        n = TreeNode("1 Airdata Computer", self.root)
        p = TreeNode("Parameters", n)
        p.children.append(TreeNode("Airspeed",p))
        p.children.append(TreeNode("Altitude",p))
        p.children.append(TreeNode("Outside Air Temperature",p))
        p.children.append(TreeNode("True Airspeed",p))
        n.children.append(p)
        d = TreeNode("Device",n)
        d.value = 14
        n.children.append(d)
        self.root.children.append(n)
        
        n = TreeNode("149 CAN-FIX Serial Converter", self.root)
        p = TreeNode("Parameters", n)
        p.children.append(TreeNode("Latitude",p))
        p.children.append(TreeNode("Longitude",p))
        p.children.append(TreeNode("Time",p))
        p.children.append(TreeNode("Date",p))
        n.children.append(p)
        d = TreeNode("Device", n)
        d.value = 12
        n.children.append(d)
        self.root.children.append(n)
        
        self.root.children.append(TreeNode("Node 3", self.root))
        self.root.children.append(TreeNode("Node 4", self.root))
        
        #NodePrint(self.root)
        
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