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
    print("Device List")
    print("-----------------------")
    for each in devices.devices:
        print(each)
        #print(each.name, '[' + hex(each.deviceType) + ']')

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

# def findDevice(did):
#     for each in devices.devices:
#         if each.DeviceId == did:
#             return each
#     return None

def fwstatus(status):
    print(status)

def load_firmware(conn, filename, node, device=None):
    import cfutil.firmware as firmware

    # If the driver type is not given then we'll try to figure it out
    if device == None:
        # Send node Identification message to node
        # TODO: We need to have our node set.
        m = can.Message(arbitration_id=0x6E0, data=[0, node])
        conn.send(m)
        while True:
            try:
                frame = conn.recv(1.0)
                if frame.arbitration_id == 0x6E0 + node:
                    msg = canfix.parseMessage(frame)
                    if msg is canfix.NodeIdentification:
                        device = devices.findDevice(msg.device, msg.model, msg.fwrev)
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
    try:
        fw = firmware.Firmware(device, filename, conn)
        fw.srcNode = 0x07
        fw.setStatusCallback(fwstatus)
        fw.destNode = node
        fw.download()
    except KeyboardInterrupt:
        fw.kill = True


def run(args):
    cmdrun = False
    try:
        conn = connection.canbus.get_connection()
        if args.list_devices == True:
            list_devices()
            cmdrun = True
        if args.firmware_file or args.firmware_node:
            cmdrun = True
            if not connection.canbus.connected:
                raise(Exception("ERROR: No valid CAN Bus connection"))
            if args.firmware_file == None:
                args.firmware_file = input("Enter Firmware Filename:")
            if args.firmware_node == None:
                args.firmware_node = int(input("Enter Node Number:"))

            if args.device_type == None and args.device_model == None and args.device_version == None:
                load_firmware(conn, args.firmware_file, args.firmware_node)
            else:
                if args.device_type == None or args.device_model == None or args.device_version == None:
                    print("ERROR: You must give device type, model and version")
                    raise(Exception("Arguments Missing"))
                d = devices.findDevice(args.device_type, args.device_model, args.device_version)
                if d == None:
                    print("ERROR: Device Not Found in Database")
                    raise(Exception("Device Not Found in Database"))
                load_firmware(conn, args.firmware_file, args.firmware_node, d)
        if args.listen == True:
            listen(conn, args.frame_count, args.raw)
            cmdrun = True
    except Exception as e:
        print(e)
#        raise(e)
    finally:
        connection.canbus.free_connection(conn)
        return cmdrun

if __name__ == "__main__":
    run(None)
