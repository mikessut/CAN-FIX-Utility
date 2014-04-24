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
import protocol
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class LiveParameterList(object):
    def __init__(self):
        self.index = []
        self.list = {}
    
    # this is the slot for the frame update signal
    def update(self, frame):
        p = protocol.parseFrame(frame)
        if isinstance(p, protocol.Parameter):
            ident = frame.id*16 + p.index
            if ident in self.list:
                self.list[ident].frame = frame
                return len(self.list) 
            self.list[ident] = p
            self.index.append(self.list[ident])
            self.index.sort()
            return 0
            
    def getItem(self, row, column):
        if column == 0:
            return self.index[row].fullName
        elif column == 1:
            return self.index[row].valueStr()
        elif column == 2:
            return self.index[row].units
    
    def rowCount(self):
        return len(self.list)

class ModelData(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.parlist = LiveParameterList()
        
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignVCenter|Qt.AlignLeft))
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
            #TODO At some point make this update only the row that was changed.
            self.dataChanged.emit(self.index(0,0),self.index(self.rowCount(), 3))
        else:
            self.modelReset.emit()
