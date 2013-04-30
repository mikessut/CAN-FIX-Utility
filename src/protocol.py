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
import struct

class NodeAlarm():
    """Represents a Node Alarm"""
    def __init__(self, frame):
        self.node = frame.id
        self.alarm = frame.data[0] + frame.data[1]*256
        self.data = frame.data[2:]

class Parameter():
    """Represents a normal parameter update frame"""
    def __init__(self, frame=None):
        if frame != None:
            self.setFrame(frame)
            
    def setFrame(self, frame):
        self.__frame = frame
        p = parameters[frame.id]
        self.name = p.name
        self.units = p.units
        self.type = p.type
        self.min = p.min
        self.max = p.max
        self.format = p.format
        self.multiplier = p.multiplier
        if self.multiplier == None:
            self.multiplier = 1
        self.indexName = p.index
        self.node = frame.data[0]
        self.index = frame.data[1]
        self.function = frame.data[2]
        self.data = bytearray(frame.data[3:])
        try:
            self.meta = p.auxdata[self.function>>4]
        except KeyError:
            self.meta = None
        if self.function | 0x04:
            self.failure = True
        else:
            self.failure = False
        if self.function | 0x02:
            self.quality = True
        else:
            self.quality = False
        if self.function | 0x01:
            self.annunciate = True
        else:
            self.annunciate = False
        self.value = self.unpack()
    
    def unpack(self):
        if self.type == "UINT, USHORT[2]": #Unusual case of the date
            x = []
            x.append(getValue("UINT", self.data[0:2],1))
            x.append(getValue("USHORT", self.data[2:3], 1))
            x.append(getValue("USHORT", self.data[3:4], 1))
        elif '[' in self.type:
            y = self.type.strip(']').split('[')
            if y[0] == 'CHAR':
                x = getValue(self.type, self.data, self.multiplier)
            else:
                x = []
                size = getTypeSize(y[0])
                for n in range(int(y[1])):
                    x.append(getValue(y[0], self.data[size*n:size*n+size], self.multiplier))
        else:
            x = getValue(self.type, self.data, self.multiplier)
        return x

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

def getTypeSize(datatype):
    table = {"BYTE":1, "WORD":2, "SHORT":1, "USHORT":1, "UINT":2,
             "INT":2, "DINT":4, "UDINT":4, "FLOAT":4, "CHAR":1}
    return table[datatype]



# This function takes the bytearray that is in data and converts it into a value.
# The table is a dictionary that contains the CAN-FIX datatype string as the
# key and a format string for the stuct.unpack function.
def getValue(datatype, data, multiplier):
    table = {"SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}
    x = None
    
    #This code handles the bit type data types
    if datatype == "BYTE":
        x = []
        for bit in range(8):
            if data[0] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        return x
    elif datatype == "WORD":
        x = []
        for bit in range(8):
            if data[0] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        for bit in range(8):
            if data[1] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        return x
    # If we get here then the data type is a numeric type or a CHAR
    try:
        x = struct.unpack(table[datatype], str(data))[0]
        return x * multiplier
    except KeyError:
        # If we get a KeyError on the dict then it's a CHAR
        if "CHAR" in datatype:
            return str(data)
        print "Ain't gotta " + datatype
        return None
        
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
            s = s + "  Format:    %s\n" % self.formatframes.append(canbus.Frame(0x183, [2, 0, 0x30, 44, 2]))
        
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

def test_print(p):
    if isinstance(p, Parameter):
        s = '[' + str(p.node) + '] ' + p.name
        if p.meta: s = s + ' ' + p.meta
        if p.value != None: s = s + ' = ' + str(p.value)
        print s
        print ' ' + p.type
        if p.indexName:
            print ' ' + p.indexName + ' ' + str(p.index+1),
        #print p.data
            
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CAN-FIX Configuration Utility Protocol Module')
    parser.add_argument('--print-info', '-p', action='store_true', help='Print Protocol Information')
    parser.add_argument('--test', '-t', action='store_true', help='Run Test')
    args = parser.parse_args()
    
    if args.print_info == True:
        print "CANFIX Protocol Version " + version
        print "Groups:"
        for each in groups:
            print "  %s %d-%d" % (each["name"], each["startid"], each["endid"])
        
        print "Parameters:"
        for each in parameters:
            print parameters[each].write()

    if args.test:
        import canbus
        frames = []
        frames.append(canbus.Frame(0x183, [2, 0, 0, 44, 5]))
        frames.append(canbus.Frame(0x183, [2, 0, 0x10, 0, 0]))
        frames.append(canbus.Frame(0x183, [2, 0, 0x20, 0xD0, 0x7]))
        frames.append(canbus.Frame(0x183, [2, 0, 0x30, 44, 2]))
        frames.append(canbus.Frame(0x184, [2, 0, 0, 0xd0, 0x7, 0, 0]))
        frames.append(canbus.Frame(0x184, [2, 0, 0, 0xff, 0xff, 255, 255]))
        frames.append(canbus.Frame(0x102, [3, 0, 0, 0x55, 0xAA]))
        frames.append(canbus.Frame(0x10E, [3, 0, 0, 0x02]))
        frames.append(canbus.Frame(0x587, [1, 0, 0, ord('7'), ord('2'), ord('7'), ord('W'), ord('B')]))
        frames.append(canbus.Frame(0x4DC, [4, 0, 0, 1, 2, 0, 0]))
        frames.append(canbus.Frame(0x581, [5, 0, 0, 0xdd, 0x07, 4, 26]))
        for f in frames:
            p = parseFrame(f)
            print '-'
            print str(f)
            test_print(p)
