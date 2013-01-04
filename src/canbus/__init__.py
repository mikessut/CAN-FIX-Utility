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


from exceptions import *
import serial
import serial.tools.list_ports
import platform
import glob
import threading
import Queue
import time
    
#def getSerialPortList():
#    """Return a list of serial ports"""
#    portList = serial.tools.list_ports.comports()
#    list = []
#    for each in portList:
#        list.append(each[0])
#        return list    

def getSerialPortList():
    system_name = platform.system()
    if system_name == "Windows":
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append(i)
                s.close()
            except serial.SerialException:
                pass
        return available
    elif system_name == "Darwin":
        # Mac
        return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
    else:
        # Assume Linux or something else
        l = []
        x = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyS*')
        for i in x:
            try:
                s = serial.Serial(i)
                l.append(i)
                s.close()
            except serial.SerialException:
                pass
        return l
                
        
# Import and add each Adapter class from the files.  There may be a way
# to do this in a loop but for now this will work.
import easy
import simulate
import network


class SendThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.getout = False
    
    def run(self):
        while(True):
            try:
                frame = sendQueue.get(timeout = 0.5)
                adapters[adapterIndex].sendFrame(frame)
            except Queue.Empty:
                pass
            except BusError:
                # TODO: Should handle some of these
                pass
            finally:
                if(self.getout):
                    break
                print "Send Thread", adapterIndex
        print "End of the Send Thread"
    
    def quit(self):
        self.getout = True

class RecvThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.getout = False
    
    def run(self):
        while(True):
            try:
                frame = adapters[adapterIndex].recvFrame()
                n = 0
                for each in recvQueueActive:
                    if each:
                        recvQueueList[n].put(frame)
                        n+=1
            except DeviceTimeout:
                pass
            except BusError:
                # TODO: Should probably handle some of these.
                pass
            finally:
                if(self.getout):
                    break
                print "Receive Thread", adapterIndex
        print "End of the Receive thread"
        
    def quit(self):
        self.getout = True

def connect(index = None, config = None):
    global adapters
    global adapterIndex
    global sendThread
    global recvThread
    
    print "canbus.connect() has been called"
    if adapterIndex != None:
        if index == None:
            #return a new Receive Queue
            pass
        else:
            #Raise an exception that we already have a connection
            pass
    else:
        if index == None:
            #Raise an exception that we have to have information
            pass
        else:
            sendThread = SendThread()
            recvThread = RecvThread()
            adapters[index].connect(config)
            adapterIndex = index
            sendThread.start()
            recvThread.start()
    return True
    
def disconnect():
    global adapters
    global adapterIndex
    global sendThread
    global recvThread
    
    if adapterIndex != None:
        try:
            adapters[adapterIndex].disconnect()
        finally:
            if sendThread:
                sendThread.quit()
                sendThread.join()
            if recvThread:
                recvThread.quit()
                recvThread.join()
            sendThread = None
            recvThread = None
            adapterIndex = None

            # I know there is a more pythonic way to do this but this is what I know.
            for each in range(len(recvQueueActive)):
                recvQueueActive[each] = False
    

        
def sendFrame(frame):
    if adapterIndex == None:
        raise BusInitError("No Connection to CAN-Bus")
    sendQueue.put(frame)

def recvFrame(index, timeout = 0.25):
    if adapterIndex == None:
        raise BusInitError("No Connection to CAN-Bus")
    if index < 0 or index > len(recvQueueList):
        raise IndexError("No Such Receive Queue")
    if recvQueueActive[index] == False:
        raise BusInitError("Queue is not active")
    
    try:
        frame = recvQueueList[index].get(timeout = timeout)
        return frame
    except Queue.Empty:
        raise DeviceTimeout()
    
def enableRecvQueue(index):
    global listLock
    global recvQueueList
    global recvQueueActive
    
    with listLock:
        if index < 0 or index > len(recvQueueActive):
            raise IndexError("No Such Receive Queue")
        else:
            recvQueueActive[index] = True
            
def disableRecvQueue(index):
    global listLock
    global recvQueueList
    global recvQueueActive
    
    with listLock:
        if index < 0 or index > recvQueueActive.len():
            raise IndexError("No Such Receive Queue")
        else:
            recvQueueActive[index] = False
            

def addRecvQueue():
    """Adds a new Queue to the recvQueueList"""
    global listLock
    global recvQueueList
    global recvQueueActive
    
    with listLock:
        newQueue = Queue.Queue()
        recvQueueList.append(newQueue)
        recvQueueActive.append(False)

adapters = []
adapters.append(easy.Adapter())
adapters.append(simulate.Adapter())
adapters.append(network.Adapter())

adapterIndex = None
sendQueue = Queue.Queue()
recvQueueList = []
recvQueueActive = []
listLock = threading.Lock()
sendThread = None
recvThread = None

for each in range(3):
    addRecvQueue()
    