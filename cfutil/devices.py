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

# This module exposes a list of all the devices that we know how to talk to.
# These devices are all defined by XML files in config.DataPath/devices
# There is one XML file per device.

import config
import os
import xml.etree.ElementTree as ET

class Device:
    """Represents a single CAN-FIX device type"""
    def __init__(self, name, id, model):
        self.name = name
        self.DeviceId = int(id, 0)
        self.modelNumber = int(model, 0)
        self.fwUpdateCode = None
        self.fwDriver = None
        self.parameters = []
        self.configuration = []
                    
def __getFirmWare(element, device):
    root = element.find("firmware_update")
    if root != None:
        try:
            code = root.attrib['code']
            driver = root.attrib['driver']
        except KeyError as key:
            print("Unable to find Firmware Code or Driver for", device.name)
        else:
            device.fwUpdateCode = int(code, 0)
            device.fwDriver = driver


def __getParameters(element, device):
    root = element.find("parameters")
    for child in root:
        if child.tag == 'parameter':
            device.parameters.append(child.attrib['id'])

def __getConfiguration(element, device):
    pass

devices = []

dirlist = os.listdir(config.DataPath + "devices")
print("Loading Devices")

for each in dirlist:
    if each[-4:] == ".xml":
        tree = ET.parse(config.DataPath + "devices/" + each)
        root = tree.getroot()
        if root.tag != "device":
            print("No device defined in", each)
            continue
        try:
            name = root.attrib['name']
            did = root.attrib['id']
            model = root.attrib['model']
        except KeyError as key:
            print("Unable to find %s in %s" % (key, each))
        else:
            newdevice = Device(name, did, model)
            __getFirmWare(root, newdevice)
            __getParameters(root, newdevice)
            __getConfiguration(root, newdevice)
            devices.append(newdevice)
            
def findDevice(device, model):
    for each in devices:
        if each.DeviceId == device and each.modelNumber == model:
            return each
    return None

if __name__ == "__main__":
    for each in devices:
        print(each.name, each.DeviceId, each.modelNumber)
        print("  FW Code =", each.fwUpdateCode)
        print("  FW Driver = ", each.fwDriver)
        print("  Parameters = ", each.parameters)
            