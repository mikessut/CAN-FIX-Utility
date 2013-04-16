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

def run(args):
    print args
    
    if args.list_devices == True:
        print
        print "Device Name [Device ID]"
        print "-----------------------"
        for each in devices.devices:
            print each.name, '[' + hex(each.DeviceId) + ']'
    if args.listen == True:
        config = {}
        config['bitrate']=args.bitrate
        config['port']=args.serial_port
        config['ipaddress']=args.ip_address
        canbus.connect(None, config, args.adapter)
        canbus.enableRecvQueue(0)
        count = 0
        while True:
            try:
                frame = canbus.recvFrame(0)
                print str(frame)
                count+=1
                if args.frame_count != 0:
                    if count > args.frame_count: break
            except canbus.exceptions.DeviceTimeout:
                pass
            
        canbus.disconnect()

if __name__ == "__main__":
    run(None)