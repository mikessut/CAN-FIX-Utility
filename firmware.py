#!/usr/bin/python

from intelhex import IntelHex
import crc
import canbus
import string
import time
import argparse
import threading

class Channels():
    """A Class to keep up with free CANFIX Channels"""
    def __init__(self):
        self.channel = [0]*16

    def GetFreeChannel(self):
        for each in range(16):
            if self.channel[each] == 0:
                return each
        return -1

    def ClearAll(self):
        for each in range(16):
            self.channel[each] = 0

    def TestFrame(self, frame):
        FirstChannel = 1760

        if frame.id >= FirstChannel and frame.id < FirstChannel+32:
            c = (frame.id - FirstChannel)/2
            self.channel[c] = 1

class Firmware():
    """A Class that represents the firmware logic."""
    def __init__(self, canbus, filename):
        """canbus is a canbus.Connection() object and filename is a string that is 
           the path to the Intel Hex file that we are downloading"""
        self.canbus = canbus
        self.ih = IntelHex(filename)
        
        cs = crc.crc16()
        for each in range(self.ih.minaddr(), self.ih.maxaddr()+1):
            cs.addByte(self.ih[each])
        self.__size = self.ih.maxaddr()+1
        self.__checksum = cs.getResult()
        self.lock = threading.Lock()
        self.__progress = 0.0
        self.__blocks = self.__size / 64 + 1
        self.__currentblock = 0
        self.__blocksize = 64
    
    def Download(self):
        data = []
        endtime = time.time() + 0.5
        while True: # Firmware load request loop
            while True: # Channel wait loop
                # Wait for messages
                # check channels
                
                now = time.time()
                if now > endtime: break
            # send firmware request
            # check response break if yes
            break; # just for now
        # Get our firmware bytes into a normal list
        for n in range(self.__blocks * self.__blocksize):
            data.append(self.ih[n])
        for block in range(self.__blocks):
            address = block * 64
            print "Buffer Fill at %d" % (address)
            self.lock.acquire()
            #self.__progress = float(n) / float(self.size)
            self.__currentblock = block
            self.lock.release()
            for n in range(self.__blocksize / 8):
                print data[address + (8*n):address + (8*n) + 8]
                self.lock.acquire()
                self.__progress = float(address + 8*n) / float(self.size)
                self.lock.release()
                
                time.sleep(0.05)
                # TODO Need to deal with the abort from the uC somewhere
            # Erase Page
            print "Erase Page Address =", address
            time.sleep(0.1)
            
            # Write Page
            print "Write Page Address =", address
            time.sleep(0.1)
            
        self.__progress = 1.0
        print "Download Complete Checksum", hex(self.__checksum), "Size", self.__size
    
    def getProgress(self):
        self.lock.acquire()
        progress = self.__progress
        self.lock.release()
        return progress
    
    def getCurrentBlock(self):
        self.lock.acquire()
        progress = self.__currentblock
        self.lock.release()
        return progress
    
    def getBlocks(self):
        return self.__blocks
        
    def getSize(self):
        return self.__size
        
    def getChecksum(self):
        return self.__checksum
        
    def Connect():
        can.connect()
        can.init()
        can.open()
        time.sleep(3)
        can.close()
    
    currentblock = property(getCurrentBlock)
    progress = property(getProgress)
    blocks = property(getBlocks)
    size = property(getSize)
    checksum = property(getChecksum)
        
class FirmwareThread(threading.Thread):
    def __init__(self, fw):
        self.fw = fw
        threading.Thread.__init__(self)
        
    def run(self):
        self.fw.Download()
        
def config():
    parser = argparse.ArgumentParser(description='CANFIX Firmware Downloader 1.0')
    parser.add_argument('--filename', '-f', nargs=1, help='Intel Hex File to Download', required=True)
    parser.add_argument('--port', '-p', nargs=1, help='Serial Port to find CANBus interface')
    args = parser.parse_args()
    args = vars(args)
    output = {}
    if args['port'] != None:
        output["portname"]= args['port'][0]
    else:
        output["portname"] = ""

    output["filename"] = args['filename'][0]

    return output


#***** MAIN ROUTINE *****
def main():
    args = config()
    can = canbus.Connection(args['portname'])
    
    fw = Firmware(can, args['filename'])
    print "Program size", fw.size
    print "Block Count", fw.blocks
    
    fwt = FirmwareThread(fw)
    fwt.start()
    
    while True:
        print fw.progress
        print "Current Block", fw.currentblock
        if not fwt.isAlive(): break
        time.sleep(0.2)
       
if __name__ == '__main__':
    main()