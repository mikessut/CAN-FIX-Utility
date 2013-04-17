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
import xml.etree.ElementTree as ET
import copy

class NodeAlarm():
    """Represents a Node Alarm"""
    def __init__(self, frame):
        self.node = frame.id
        self.alarm = frame.data[0] + frame.data[1]*256
        self.data = frame.data[2:]

class Parameter():
    """Represents a normal parameter update frame"""
    def __init__(self, frame):
        p = parameters[frame.id]
        self.name = p.name
        self.units = p.units
        self.min = p.min
        self.max = p.max
        self.format = p.format

class TwoWayMsg():
    """Represents 2 Way communication channel data"""
    def __init__(self, frame):
        self.channel = (frame.id - 1760) /2
        self.data = frame.data
        if frame.id % 2 == 0:
            self.type = "Request"
        else:
            self.type = "Response"

class NodeSpecific():
    """Represents a Node Specific Message"""
    def __init(self, frame):
        self.sendNode = frame.id -1792
        self.destNode = frame.data[0]
        self.controlCode = frame.data[1]
        self.data = frame.data[2:]
        
def parseFrame(frame):
    """Determine what type of frame is given and return an object
       that represents what that frame is"""
    if frame.id < 256:
        return NodeAlarm(frame)
    elif frame.id < 1760:
        return Parameter(frame)
    elif frame.id < 1792:
        return TwoWayMsg(frame)
    elif frame.id < 2048:
        return NodeSpecific(frame)
    else:
        return None

        
def __getText(element, text):
    try:
        return element.find(text).text
    except AttributeError:
        return None

def __getFloat(s):
    """Take string 's,' remove any commas and return a float"""
    if s:
        return float(s.replace(",",""))
    else:
        return None


class ParameterDef():
    def __init__(self, name):
        self.name = name
        self.units = None
        self.type = None
        self.multiplier = 1.0
        self.offset = None
        self.min = None
        self.max = None
        self.index = None
        self.format = None
        self.auxdata = {}
        self.remarks = []
    
    def write(self):
        s = "(0x%03X, %d) %s\n" % (self.id, self.id, self.name)
        if self.type:
            s = s + "  Data Type: %s\n" % self.type
        if self.units:
            if self.multiplier == 1.0:
                s = s + "  Units:     %s\n" % self.units
            else:
                s = s + "  Units:     %s x %s\n" % (self.units, str(self.multiplier))
        if self.offset:
            s = s + "  Offset:    %s\n" % str(self.offset)
        if self.min:
            s = s + "  Min:       %s\n" % str(self.min)
        if self.max:
            s = s + "  Max:       %s\n" % str(self.max)
        if self.format:
            s = s + "  Format:    %s\n" % self.format
        if self.index:
            s = s + "  Index:     %s\n" % self.index
        if self.auxdata:
            s = s + "  Auxilliary Data:\n"
            for each in self.auxdata:
                s = s + "   0x%02X - %s\n" % (each, self.auxdata[each])
        if self.remarks:
            s = s + "  Remarks:\n"
            for each in self.remarks:
                s = s + "    " + each + "\n"
        return s
    
    
tree = ET.parse(config.DataPath + "canfix.xml")
root = tree.getroot()            
if root.tag != "protocol":
    raise ValueError("Root Tag is not protocol'")

child = root.find("name")
if child.text != "CANFIX":
    raise ValueError("Not a CANFIX Protocol File")

child = root.find("version")
version = child.text

groups = []
parameters = {}

def __add_group(element):
    child = element.find("name")
    x = {}
    x['name'] = element.find("name").text
    x['startid'] = int(element.find("startid").text)
    x['endid'] = int(element.find("endid").text)
    groups.append(x)

def __add_parameter(element):
    pid = int(element.find("id").text)
    count = int(element.find("count").text)
    
    p = ParameterDef(element.find("name").text)
    p.units = __getText(element, "units")
    p.format = __getText(element, "format")
    p.type = __getText(element, "type")
    p.multiplier = __getFloat(__getText(element, "multiplier"))
    p.offset = __getFloat(__getText(element, "offset"))
    p.min = __getFloat(__getText(element, "min"))
    p.max = __getFloat(__getText(element, "max"))
    p.index = __getText(element, "index")
    
    l = element.findall('aux')
    for each in l:
        p.auxdata[int(each.attrib['id'])] = each.text
    l = element.findall('remarks')
    
    for each in l:
        p.remarks.append(each.text)

    if count > 1:
        for n in range(count):
            np = copy.copy(p)
            np.name = p.name + " #" + str(n+1)
            np.id = pid + n
            parameters[pid+n] = np
    else:
        p.id = pid
        parameters[pid] = p
    
for child in root:
    if child.tag == "group":
        __add_group(child)
    elif child.tag == "parameter":
        __add_parameter(child)

def getGroup(id):
    for each in groups:
        if id >= each['startid'] and id <= each['endid']:
            return each
            
if __name__ == "__main__":
    print "CANFIX Protocol Version " + version
    print "Groups:"
    for each in groups:
        print "  %s %d-%d" % (each["name"], each["startid"], each["endid"])
    
    print "Parameters:"
    for each in parameters:
        print parameters[each].write()

    
