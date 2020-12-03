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
        print(each.name, '[' + hex(each.deviceType) + ']')

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
        except:
            print(str(msg))

def findDevice(did):
    for each in devices.devices:
        if each.DeviceId == did:
            return each
    return None

def fwstatus(status):
    print(status)

def load_firmware(conn, filename, node, driver=None):
    import cfutil.firmware as firmware

    print("Load firmware {}, {}, {}".format(filename, node, driver))
    # If the driver type is not given then we'll try to find it
    if driver == None:
        # Send node Identification message to node
        m = can.Message(arbitration_id=0x6E0, data=[0, node])
        conn.send(m)
        while True:
            try:
                frame = conn.recv()
                if frame.arbitration_id == 0x6E0 + node:
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
        fw = firmware.Firmware(device.fwDriver, filename, conn)
    else:
        fw = firmware.Firmware(driver, filename, conn)
    fw.setStatusCallback(fwstatus)
    fw.download(node)

def run(args):
    cmdrun = False
    try:
        conn = connection.canbus.get_connection()
        print(args.firmware_file)
        print(args.firmware_node)
        print(args.firmware_driver)
        if args.list_devices == True:
            list_devices()
            cmdrun = True
        if args.firmware_file or args.firmware_node:
            if args.firmware_file == None:
                args.firmware_file = input("Enter Firmware Filename:")
            if args.firmware_node == None:
                args.firmware_node = int(input("Enter Node Number:"))
            if args.firmware_driver == None:
                load_firmware(conn, args.firmware_file, args.firmware_node)
            else:
                load_firmware(conn, args.firmware_file, args.firmware_node, args.firmware_driver)
            cmdrun = True
        if args.listen == True:
            listen(conn, args.frame_count, args.raw)
            cmdrun = True
    except Exception as e:
        print(e)
        raise(e)
    # finally:
    #     connection.canbus.free_connection(conn)
    #     return cmdrun

if __name__ == "__main__":
    run(None)
