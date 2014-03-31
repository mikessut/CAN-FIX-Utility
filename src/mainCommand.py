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

import canbus
import config
import devices
import protocol

can = None

def get_adapter(args):
    if args.adapter:
        return args.adapter
    else:
        while(True):
            n = 1
            for each in canbus.adapterList:
                print n, ") -", each.name
                n = n+1
            print "x ) - Cancel"
            x = raw_input("Select Adapter: ")
            if x == "x":
                return
            try:
                return canbus.adapterList[int(x)-1].shortname
            except:
                pass

def connect(args):
    global can
    
    if can == None:
        print "Connect()"
        a = get_adapter(args)
        can = canbus.Connection(a)
        if args.ip_address:
            can.ipaddress = args.ip_address
        if args.serial_port:
            can.device = args.serial_port
        can.bitrate = int(args.bitrate)
        can.connect()

def disconnect():
    global can
    
    if can != None:
        can.disconnect()
        can = None

def list_devices():
    print "Device Name [Device ID]"
    print "-----------------------"
    for each in devices.devices:
        print each.name, '[' + hex(each.DeviceId) + ']'

def listen(frame_count):
    global can
    count = 0
    while True:
        try:
            frame = can.recvFrame()
            #print str(frame) + protocol.parameters[frame.id].name
            x = protocol.parseFrame(frame)
            print str(frame)
            count+=1
            if frame_count != 0:
                if count > frame_count: break
        except canbus.exceptions.DeviceTimeout:
            pass
        except KeyboardInterrupt:
            break
    

def run(args):
    global can
    
    try:
        if args.list_devices == True:
            list_devices()
        if args.listen == True:
            connect(args)
            listen(args.frame_count)
    except:
        disconnect()
        raise
    disconnect()
        
if __name__ == "__main__":
    run(None)