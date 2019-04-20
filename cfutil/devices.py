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

import os
import logging
import json
import cfutil.config as config

log = logging.getLogger(__name__)

class Device:
    """Represents a single CAN-FIX device type"""
    def __init__(self, name, id, model, version):
        self.name = name
        self.deviceId = int(id, 0)
        self.modelNumber = int(model, 0)
        self.version = int(version, 0)
        self.fwUpdateCode = None
        self.fwDriver = None
        self.parameters = []
        self.configuration = []

    def __str__(self):
        return "{} id={}, model={}, version={}".format(self.name, self.deviceId, self.modelNumber, self.version)

devices = []

dirlist = os.listdir(config.DataPath + "devices")
log.debug("Loading Devices")

for filename in dirlist:
    if filename[-5:] == ".json":
        with open(config.DataPath + "devices/" + filename) as json_file:
            d = json.load(json_file)
        try: # These must exist
            name = d["name"]
            did = d["id"]
            model = d["model"]
            version = d["version"]
        except KeyError as e:
            log.warn("Problem with device file {}:{}".format(config.DataPath + "devices/" + filename, e))
        newdevice = Device(name, did, model, version)
        newdevice.fwUpdateCode = d.get("firmware_code")
        newdevice.fwDriver = d.get("firmware_driver")
        # newdevice.parameters = []
        # newdevice.configuration = []

        devices.append(newdevice)
        log.info(str(newdevice))

def findDevice(device, model, version):
    for each in devices:
        if each.deviceId == device and each.modelNumber == model and each.version == version:
            return each
    return None

if __name__ == "__main__":
    for each in devices:
        print(each.name, each.deviceId, each.modelNumber)
        print("  FW Code =", each.fwUpdateCode)
        print("  FW Driver = ", each.fwDriver)
        print("  Parameters = ", each.parameters)
