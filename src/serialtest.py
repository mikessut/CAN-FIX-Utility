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

# This program pretends to be the CAN-FIX-USB adapter for testing purposes.

import serial
import argparse

class Simulator():
    def __init__(self, args):
        self.getout = False
        self.count = 0
        if args.port:
            self.port = args.port
        else:
            self.port = 0
        self.verbose = args.verbose

    def send(self, ch):
        """This function works just like serial.write() except that it
           will print the data if --verbose was set"""
        if self.verbose:
            print(">", ch)
        self.ser.write(ch)
        
    def recv(self):
        """This function works just like serial.read() except that it
           will print the data if --verbose was set"""
        ch = self.ser.read()
        if self.verbose:
            print("<", ch)
        return ch
 
    def start(self):
        self.ser = serial.Serial(self.port, 115200, timeout = 0.25)
        s = ""

        while 1:
            if self.getout: break
            x = self.recv()
            if len(x) == 0:
                self.respond()
                continue
            s = s + x
            if x == '\n':
                if s == 'K\n':
                    self.send('k\n')
                elif s[0] == 'B':
                    self.send('b\n')
                elif s == 'O\n':
                    self.send('o\n')
                elif s == 'C\n':
                    self.send('c\n')
                elif s[0] == 'W':
                    self.send('w\n')
                print(s, end=' ')
                s = ""
    
    def respond(self, data=""):
        self.count += 1
        if self.count % 4 == 0:
            self.send("r183:0100005603\n")
                
    def quit(self):
        self.getout = True
        
def main():
    parser = argparse.ArgumentParser(description='CAN-FIX Simulation / Testing Utility')
    parser.add_argument('--port', '-p', help='Serial Device to Connect')
    parser.add_argument('--verbose','-v', action='store_true', help='Send data to STDOUT')
    
    args = parser.parse_args()
    
    sim = Simulator(args)
    try:
        sim.start()
    except KeyboardInterrupt:
        sim.quit()
        
        
main()