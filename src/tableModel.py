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

import canbus
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Parameter(object):
    def __init__(self, ident, name, value):
        self.ident = ident
        self.name = name
        self.value = value
        self.status = ""
    
    def __cmp__(self, other):
        if self.ident > other.ident:
            return 1
        elif self.ident < other.ident:
            return -1
        else:
            return 0

class ModelData(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.pindex = []
        self.plist = {}
     
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignVCenter|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        column = index.column()
        row = index.row()
        if column == 0:
            return self.pindex[row].name
        elif column == 1:
            return self.pindex[row].value
        elif column == 2:
            return self.pindex[row].status
        return QVariant(item)
    
    def rowCount(self, parent = QModelIndex()):
        return len(self.plist)
    
    def columnCount(self, parent = QModelIndex()):
        return 3
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0:
                return QVariant("Name")
            elif col == 1: 
                return QVariant("Value")
            elif col == 2:
                return QVariant("Status")
            else:
                return QVariant("")
        #if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #    return QVariant(self.parlist[col].id)
        return QVariant()
    
    def edit(self, index):
        print("Edit Data Row %d" % index.row())

    def parameterAdd(self, p):
        ident = p.identifier*16 + p.index
        self.plist[ident] = Parameter(ident, p.fullName, p.valueStr)
        
        self.pindex.append(self.plist[ident])
        self.pindex.sort()
        self.modelReset.emit()

    def parameterChange(self, p):
        ident = p.identifier*16 + p.index
        self.plist[ident].value = p.valueStr()
        #TODO At some point make this update only the row that was changed.
        self.dataChanged.emit(self.index(0,1),self.index(self.rowCount(), 2))