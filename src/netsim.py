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
        
    def stop(self):
        print "Stopping Thread", self.name
        self.__stop.set()
        
    def stopped(self):
        return self.__stop.isSet()
        

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
                    self.socket.send(str(result))
        
        print "ServerSendThread Quitting"
    

        
class ServerRecvThread(StoppableThread):
    """This thread handles inbound CAN frames from the client"""
    def __init__(self, socket, name):
        super(ServerRecvThread, self).__init__(name)
        self.socket = socket
    
    def run(self):
        while True:
            try:
                result = self.socket.recv(1024)
            except socket.timeout:
                if self.stopped(): break
            else:
                if not result: break
                print result
        #self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print "ServerRecvThread Quitting"


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
        if self.passcount == self.interval:
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
            #print self.value
            return self.getFrame()
        
    
class NodeThread(StoppableThread):
    def __init__(self, nodeID, sendQueue, name=None):
        super(NodeThread, self).__init__(name)
        self.nodeID = nodeID
        self.sendQueue = sendQueue
        self.deviceID = 0x00
        self.model = 0x00
        self.version = 0x0000
        self.period = 1.000
        self.enabled = False
        self.parameters = []
        self.frameQueue = Queue.Queue()

    def run(self):
        while True:
            time.sleep(self.period)
            if self.stopped(): break
            for each in self.parameters:
                if each.enabled:
                    each.node = self.nodeID
                    result = each.process()
                    if result:
                        xmit = "r"
                        xmit = xmit + '%03X' % result.id
                        xmit = xmit + ':'
                        for each in result.data:
                            xmit = xmit + '%02X' % each
                        xmit = xmit + '\n'
                        self.sendQueue.put(xmit)
            #TODO Deal with incoming messages here.
            
        
        print "NodeThread Quitting"

class CommandThread(threading.Thread):
    def __init__(self):
        super(CommandThread, self).__init__()
        
    def run(self):
        while True:
            s = raw_input('>')
            if s == 'exit':
                break
        
if __name__ == "__main__":
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
            print 'got connection from', addr
            
            st = ServerSendThread(c, name="Send Thread")
            rt = ServerRecvThread(c, name="Receive Thread")
            st.start()
            rt.start()
            nt = NodeThread(10, st.sendQueue, name="Air Data Node")
            p = NodeParameter("indicated airspeed")
            p.meanValue = 180.0
            nt.parameters.append(p)
            p = NodeParameter("indicated altitude")
            p.meanValue = 8500
            p.noise = 0.001
            nt.parameters.append(p)
            p = NodeParameter("time")
            nt.parameters.append(p)
            p = NodeParameter("date")
            nt.parameters.append(p)
            p = NodeParameter("Aircraft Identifier")
            p.interval = 10
            nt.parameters.append(p)
            nt.start()
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
