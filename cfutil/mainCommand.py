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

# Module interprets the command line arguments and performs the job(s) given

import can
import canfix
import cfutil.config as config
import cfutil.connection as connection
import cfutil.devices as devices


def list_devices():
    print("Device Name [Device ID]")
    print("-----------------------")
    for each in devices.devices:
        print(each.name, '[' + hex(each.DeviceId) + ']')

def listen(conn, msg_count, raw):
    count = 0
    while True:
        try:
            msg = conn.recv(1.0)
            if msg:
                #print(str(msg) + canfix.parameters[msg.arbitration_id].name)
                x = canfix.parseMessage(msg)
                if raw:
                    print(str(msg))
                else:
                    print(canfix.Parameter(msg))
                count+=1
                if msg_count != 0:
                    if count > msg_count: break
        except KeyboardInterrupt:
            break

def findDevice(did):
    for each in devices.devices:
        if each.DeviceId == did:
            return each
    return None

def fwstatus(status):
    print(status)

def load_firmware(conn, filename, node):
    m = can.Message(arbitration_id=0x700, data=[node, 0])
    conn.send(m)
    while True:
        try:
            frame = conn.recv()
            if frame.arbitration_id == 0x700 + node:
                device = findDevice(frame.data[3])
                if device:
                    print("Found", device.name, "At Node", node)
                    print("Using Firmware Driver", device.fwDriver)
                else:
                    print("Unknown Device at that node")
                    return
        except canbus.exceptions.DeviceTimeout:
            break
        except KeyboardInterrupt:
            return
    fw = firmware.Firmware(device.fwDriver, filename, can)
    fw.setStatusCallback(fwstatus)
    fw.download(node)

def run(args):
    try:
        conn = connection.connect()
        if args.list_devices == True:
            list_devices()
        if args.firmware_file or args.firmware_node:
            import firmware
            if args.firmware_file == None:
                args.firmware_file = input("Enter Firmware Filename:")
            if args.firmware_node == None:
                args.firmware_node = int(input("Enter Node Number:"))
            load_firmware(args.firmware_file, args.firmware_node)
        if args.listen == True:
            listen(conn, args.frame_count, args.raw)


    finally:
        connection.disconnect(conn)

if __name__ == "__main__":
    run(None)
