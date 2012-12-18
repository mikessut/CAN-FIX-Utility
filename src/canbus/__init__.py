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


# This module is to abstract the interface between the code and the
# CANBus communication adapters.

class BusError(Exception):
    """Base class for exceptions in this module"""
    pass

class BusInitError(BusError):
    """CAN Bus Initialization Error"""
    def __init__(self, msg):
        self.msg = msg

class BusReadError(BusError):
    """CAN Bus Read Error"""
    def __init__(self, msg):
        self.msg = msg

class BusWriteError(BusError):
    """CAN Bus Write Error"""
    def __init__(self, msg):
        self.msg = msg

class DeviceTimeout(Exception):
    """Device Timeout Exception"""
    pass

import serial
import serial.tools.list_ports
import threading
import Queue
import os
    
def getSerialPortList():
    """Return a list of serial ports"""
    portList = serial.tools.list_ports.comports()
    list = []
    for each in portList:
        list.append(each[0])
        return list    

class SendThread(threading.Thread):
    def __init__(self):
        self.getout = False
    
    def run(self):
        while(True):
            os.sleep(1)
            if(self.getout):
                break
            print "Okay"
    
    def quit(self):
        self.getout = True
   
# Import and add each Adapter class from the files.  There may be a way
# to do this in a loop but for now this will work.
import easy
import simulate
import network

adapters = []
adapters.append(easy.Adapter())
adapters.append(simulate.Adapter())
adapters.append(network.Adapter())

adapterIndex = None
sendQueue = Queue.Queue()
recvQueueList = []
listLock = threading.Lock()
sendThread = SendThread()
            

def connect(index = None, config = None):
    global adapters
    global adapterIndex
    
    print "canbus.connect() has been called"
    if adapterIndex != None:
        if index == None:
            #return a new Queue
            pass
        else:
            #Raise an exception that we already have a connection
            pass
    else:
        if index == None:
            #Raise an exception that we have to have information
            pass
        else:
            sendThread.start()
            adpaters[index].connect()
            adapterIndex = index
    
def disconnect(queueIndex):
    global adapters
    global adapterIndex
    
    if adapterIndex != None:
        adpaters[adapterIndex].disconnect()
        adapterIndex = None

def sendFrame(frame):
    if adapterIndex == None:
        raise BussInitError("No Connection to CAN-Bus")
    sendQueue.put(frame)

def recvFrame(index, frame, timeout = 0.25):
    if adapterIndex == None:
        raise BussInitError("No Connection to CAN-Bus")
    
    adpaters[adapterIndex].sendFrame(frame) 

def addRecvQueue():
    """Adds a new Queue to the recvQueueList"""
    global listLock
    global recvQueueList
    
    with listLock:
        newQueue = Queue()
        recvQueueList.append(newQueue)
        return newQueue
    