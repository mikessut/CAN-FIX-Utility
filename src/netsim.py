#!/usr/bin/env python

#  CAN-FIX Utilities - An Open Source CAN FIX Utility Package 
#  Copyright (c) 2014 Phil Birkelbach
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

import socket
import threading
import protocol
import canbus
import time
import Queue
import sys
import random

class StoppableThread(threading.Thread):
    def __init__(self, name):
        super(StoppableThread, self).__init__(name=name)
        self.__stop = threading.Event()
        self.__enable = threading.Event()
        
    def stop(self):
        if _debug: print "Stopping Thread", self.name
        self.__stop.set()
        
    def stopped(self):
        return self.__stop.isSet()
    
    def enable(self):
        self.__enable.set()
    
    def disable(self):
        self.__enable.clear()
        
    def enabled(self):
        return self.__enable.isSet()
    

class ServerSendThread(StoppableThread):
    """This thread handles outbound CAN frames to the client"""
    def __init__(self, socket, name=None):
        super(ServerSendThread, self).__init__(name)
        self.socket = socket
        self.sendQueue = Queue.Queue()
    
    def run(self):
        while True:
            try:
                result = self.sendQueue.get(timeout=1.0)
            except Queue.Empty:
                if self.stopped(): break
            else:
                if result:
                   
                    if isinstance(result, canbus.Frame):
                        s = frameToString(result)
                    else:
                        s = str(result)
                    if _debug:
                        print "-> %s" % (s,),
                    self.socket.send(s)
        
        if _debug: print "ServerSendThread Quitting"
    

        
class ServerRecvThread(StoppableThread):
    """This thread handles inbound messages from the client"""
    def __init__(self, socket, name):
        super(ServerRecvThread, self).__init__(name)
        self.socket = socket
        self.nodelist = []
        self.sendQueue = None
        
    def run(self):
        while True:
            try:
                result = self.socket.recv(1024)
            except socket.timeout:
                if self.stopped(): break
            else:
                if not result: break
                clist = result.split('\n')
                for each in clist:
                    self.handleCommand(each)
        self.socket.close()
        if _debug: print "ServerRecvThread Quitting"

    def handleCommand(self, command):
        if len(command) <= 0: return
        if _debug:
            print "<-", command
        if command[0]=='B': # Bitrate set
            if _debug: print "Set Bitrate to", command[1:-1]
        elif command[0]=='O': # Open Port
            if _debug: print "Open CAN Connection"
            for node in self.nodelist:
                node.enable()
        elif command[0]=='C': # Open Port
            if _debug: print "Close CAN Connection"
            for node in self.nodelist:
                node.disable()
        elif command[0]=='E': # Error Request
            if _debug: print "Error Request"
        elif command[0]=='W': # Inbound Frame
            # Send the response and put the frame into
            # each nodes inbound frame Queue
            #self.sendQueue.put('w\n')
            f = stringToFrame(command)
            for each in self.nodelist:
                each.frameQueue.put(f)
        else:
            pass
    

class NodeParameter(protocol.Parameter):
    def __init__(self, name=None):
        super(NodeParameter, self).__init__()
        self.enabled = True
        self.interval = 1
        self.passcount = 0
        self.meanValue = 0
        self.noise = 0.005
        if name:
            self.name = name
    
    def process(self):
        self.passcount += 1
        if self.passcount >= self.interval:
            self.passcount = 0
            if self.identifier == 0x580: # Time
                t = time.struct_time(time.gmtime())
                self.value = [t[3], t[4], t[5]]
            elif self.identifier == 0x581: # Date
                t = time.struct_time(time.gmtime())
                self.value = [t[0], t[1], t[2]]
            elif self.identifier == 0x587: # Aircraft ID
                self.value = ['7', '2', '7', 'W', 'B']
            else:
                self.value = self.meanValue + (random.random() - 0.5) *2 * (self.noise * self.meanValue)
            return self.getFrame()
    
    def report(self):
        """Calling this function will make us report
           our information on the next pass"""
        self.passcount = self.interval

# Node states
OFF = 0x00
NORMAL = 0x01
FW_UPDATE = 0x02
    
class NodeThread(StoppableThread):
    def __init__(self, nodeID, sendQueue, name=None):
        super(NodeThread, self).__init__(name)
        self.nodeID = nodeID
        self.sendQueue = sendQueue
        self.deviceID = 0x00
        self.model = 0x000000
        self.version = 0x00
        self.FWVCode = 0x00
        self.period = 1.000 # How often we update parameters
        self.parameters = []
        self.frameQueue = Queue.Queue()
        self.state = NORMAL

    def run(self):
        while True:
            if self.enabled():
                # Process any incoming frames that apply to us
                # We use the frame queue timeout as the period timing
                try:
                    frame = self.frameQueue.get(timeout=self.period)
                    self.handleFrame(frame)
                except Queue.Empty:
                    # When the queue is empty the timeout has expired
                    if self.stopped(): break
                    # Process all the parameters
                    for each in self.parameters:
                        if each.enabled:
                            each.node = self.nodeID
                            result = each.process()
                            if result:
                                xmit = frameToString(result)
                                self.sendQueue.put(xmit)
            else:
                time.sleep(self.period)
                if self.stopped(): break
            
        if _debug: print self.name, "Quitting"
        
    def handleFrame(self, frame):
        if self.state == NORMAL:
            if frame.id >= 0x700 and frame.data[0] == self.nodeID:
                # We start a response frame in case we need it
                f = canbus.Frame(self.nodeID + 0x700, [frame.id - 0x700, frame.data[1]])
                cmd = frame.data[1]
                if cmd == 0: #Node identification
                    f.data.extend([0x01, self.deviceID & 0xFF, 
                                   self.version & 0xFF, self.model & 0xFF,
                                   self.model >> 8 & 0xFF, self.model >> 16 & 0xFF])
                elif cmd == 1: # Bitrate Set Command
                    return None
                elif cmd == 2: # Node Set Command
                    self.nodeID = frame.data[2]
                    f.data.append(0x00)
                #TODO: Fix these so they work??
                elif cmd == 3: # Disable Parameter
                    return None
                elif cmd == 4: # Enable Parameter
                    return None
                elif cmd == 5: # Node Report
                    for each in self.parameters:
                        each.report()
                    return None
                elif cmd == 7: # Firmware Update
                    FCode = frame.data[3]<<8 | frame.data[2]
                    if FCode == self.FWVCode:
                        self.FWChannel = frame.data[4]
                        f.data.append(0x00)
                        print "Firmware Update Received", hex(FCode), hex(self.FWVCode)
                        self.state = FW_UPDATE
                    else:
                        return None # FWCode doesn't match don't send response.
                self.sendQueue.put(f)
                
        elif self.state == FW_UPDATE: #We're going to emulate AT328 Firmware update
            if frame.id == (0x6E0 + self.FWChannel*2):
                f = canbus.Frame(0x6E0 + self.FWChannel*2 + 1, frame.data)
                if self.fw_length > 0: #Indicates we are writing buffer data
                    self.fw_length-=len(frame.data)/2
                    if self.fw_length <= 0:
                        pass
                        #print "No more data"
                else: #Waiting for firmware command
                    if frame.data[0] == 1: #Write to Buffer command
                        self.fw_address = frame.data[2]<<8 | frame.data[1]
                        self.fw_length = frame.data[3]
                        #print "Buffer Write", self.fw_address, self.fw_length
                    elif frame.data[0] == 2: #Erase Page Command
                        self.fw_address = frame.data[2]<<8 | frame.data[1]
                        #print "Erase Page", self.fw_address
                    elif frame.data[0] == 3: #Write to Flash
                        self.fw_address = frame.data[2]<<8 | frame.data[1]
                        #print "Write Page", self.fw_address
                    elif frame.data[0] == 4: #Abort
                        print "Abort"
                    elif frame.data[0] == 5: #Complete Command
                        crc = frame.data[2]<<8 | frame.data[1]
                        length = frame.data[4]<<8 | frame.data[3]
                        #print "Firmware Load Complete", crc, length
                        self.state = NORMAL
                return f
        return None

class CommandThread(threading.Thread):
    def __init__(self):
        super(CommandThread, self).__init__()
        
    def run(self):
        while True:
            s = raw_input('>')
            if s == 'exit':
                break

def stringToFrame(s):
    """Converts a String from the clien to a canbus frame"""
    data= []
    for n in range((len(s)-5)/2):
        data.append(int(s[5+n*2:7+n*2], 16))
    f = canbus.Frame(int(s[1:4], 16), data)
    return f

def frameToString(f):
    """Converts a canbus frame into the string that we send
       to the client"""
    s = "r"
    s = s + '%03X' % f.id
    s = s + ':'
    for each in f.data:
        s = s + "%02X" % each
    s = s + '\n'
    return s

nodelist = []

def nodeListConfig(sendthread):
    l = []
    nt = NodeThread(179, sendthread.sendQueue, name="Air Data Node")
    nt.deviceID = 179
    nt.model = 0x0A0B0C
    nt.version = 0xEE
    p = NodeParameter("indicated airspeed")
    p.meanValue = 180.0
    nt.parameters.append(p)
    p = NodeParameter("indicated altitude")
    p.meanValue = 8500
    p.noise = 0.001
    nt.parameters.append(p)
    p = NodeParameter("static air temperature")
    p.meanValue = 22
    p.noise = 0.001
    nt.parameters.append(p)
    l.append(nt)
    
    nt = NodeThread(40, sendthread.sendQueue, name="System Data Node")
    nt.deviceID = 41
    nt.model = 0x0D0E0F
    nt.version = 0x02
    p = NodeParameter("time")
    nt.parameters.append(p)
    p = NodeParameter("date")
    p.interval = 30
    p.report()
    nt.parameters.append(p)
    p = NodeParameter("Aircraft Identifier")
    p.interval = 10
    p.report()
    nt.parameters.append(p)
    l.append(nt)
    
    nt = NodeThread(0x40, sendthread.sendQueue, name="Engine Data Node")
    nt.deviceID = 0x40
    nt.model = 0xABCDEF
    nt.version = 0x03
    p = NodeParameter("Cylinder Head Temperature #1")
    p.index = 0
    p.meanValue = 190
    nt.parameters.append(p)
    p = NodeParameter("Cylinder Head Temperature #1")
    p.index = 1
    p.meanValue = 190
    nt.parameters.append(p)
    p = NodeParameter("Cylinder Head Temperature #1")
    p.index = 2
    p.meanValue = 190
    nt.parameters.append(p)
    p = NodeParameter("Cylinder Head Temperature #1")
    p.index = 3
    p.meanValue = 190
    nt.parameters.append(p)
    p = NodeParameter("Exhaust Gas Temperature #1")
    p.index = 0
    p.meanValue = 700
    nt.parameters.append(p)
    p = NodeParameter("Exhaust Gas Temperature #1")
    p.index = 1
    p.meanValue = 700
    nt.parameters.append(p)
    p = NodeParameter("Exhaust Gas Temperature #1")
    p.index = 2
    p.meanValue = 700
    nt.parameters.append(p)
    p = NodeParameter("Exhaust Gas Temperature #1")
    p.index = 3
    p.meanValue = 700
    nt.parameters.append(p)
    p = NodeParameter("Oil Temperature #1")
    p.meanValue = 95
    nt.parameters.append(p)
    p = NodeParameter("Oil Pressure #1")
    p.meanValue = 70
    nt.parameters.append(p)
    p = NodeParameter("N1 or Engine RPM #1")
    p.meanValue = 2450
    p.noise = 0.001
    nt.parameters.append(p)
    p = NodeParameter("Manifold Pressure #1")
    p.meanValue = 24.50
    p.noise=0.001
    nt.parameters.append(p)
    nt.period = 0.9
    l.append(nt)
    
    return l

_debug = False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CAN-FIX Configuration Utility')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug Mode')
    args = parser.parse_args()
    if args.debug:
        _debug = True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "0.0.0.0"
        port = 63349 #NEFIX on keypad
        s.bind((host, port))
    except socket.error, msg:
        print "Failed to create socket", msg
        sys.exit(-1)

    s.settimeout(1.0)
    s.listen(5)
    ct = CommandThread()
    ct.start()
        
    while True:
        try:
            c, addr = s.accept()
        except socket.timeout:
            if not ct.is_alive():
                tlist = threading.enumerate()
                for each in tlist:
                    if isinstance(each, StoppableThread):
                        each.stop()
                break
        else:
            c.settimeout(1.0)
            if _debug: print 'got connection from', addr
            st = ServerSendThread(c, name="Send Thread")
            rt = ServerRecvThread(c, name="Receive Thread")
            nodelist = nodeListConfig(st)
            rt.sendQueue = st.sendQueue
            st.start()
            rt.start()
            rt.nodelist = nodelist
            for each in nodelist:
                each.start()
            while True:
                time.sleep(1.0)
                if not ct.is_alive() or not rt.is_alive():
                    tlist = threading.enumerate()
                    for each in tlist:
                        if isinstance(each, StoppableThread):
                            each.stop()
                    break
    s.close()
    sys.exit()
