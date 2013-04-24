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
import devices
import protocol

def list_devices():
    print
    print "Device Name [Device ID]"
    print "-----------------------"
    for each in devices.devices:
        print each.name, '[' + hex(each.DeviceId) + ']'

def listen(frame_count, config, adapter):
    canbus.connect(None, config, adapter)
    canbus.enableRecvQueue(0)
    count = 0
    while True:
        try:
            frame = canbus.recvFrame(0)
            #print str(frame) + protocol.parameters[frame.id].name
            x = protocol.parseFrame(frame)
            print '-'
            print str(frame)
            protocol.test_print(x)
            count+=1
            if frame_count != 0:
                if count > frame_count: break
        except canbus.exceptions.DeviceTimeout:
            pass
        except KeyboardInterrupt:
            break
    canbus.disconnect()
    

def run(args):
    try:
        print args
        
        if args.list_devices == True:
            list_devices()
        if args.listen == True:
            config = {}
            config['bitrate']=args.bitrate
            config['port']=args.serial_port
            config['ipaddress']=args.ip_address
            listen(args.frame_count, config, args.adapter)
    except:
        canbus.disconnect()
        raise
        
if __name__ == "__main__":
    run(None)