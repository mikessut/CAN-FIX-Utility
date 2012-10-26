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

        if frame["id"] >= FirstChannel and frame["id"] < FirstChannel+32:
            c = (frame.id - FirstChannel)/2
            self.channel[c] = 1

class Firmware():
    """A Class that represents the firmware logic."""
    def __init__(self, canbus, filename, srcnode=247):
        """canbus is a canbus.Connection() object and filename is a string that is 
           the path to the Intel Hex file that we are downloading"""
        self.__canbus = canbus
        self.ih = IntelHex(filename)
        self.__srcnode = srcnode

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
        self.kill = False

    # Download support functions
    def __tryChannel(self, ch):
        """Waits for a half a second to see if there is any traffic on any
           of the channels"""
        result = self.__canbus.error()
        if result != 0x00:
            self.__canbus.close()
            self.__canbus.open()
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                ch.TestFrame(rframe)
                now = time.time()
                if now > endtime: break

    def __tryFirmwareReq(self, ch, node):
        """Requests a firmware load, waits for 1/2 a second and determines
           if the response is correct and if so returns True returns
           False on timeout"""
        channel = ch.GetFreeChannel()
        sframe = {}
        sframe["id"] = 1792 + self.__srcnode
        sframe["data"] = []
        sframe["data"].append(node)
        sframe["data"].append(7)
        sframe["data"].append(1)
        sframe["data"].append(0xF7)
        sframe["data"].append(channel)
        self.__canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        ch.ClearAll()
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe["id"] == (1792 + node) and \
                   rframe["data"][0] == self.__srcnode: break
                now = time.time()
                if now > endtime: return False
        return True

    def __fillBuffer(self, ch, address, data):
        sframe = {}
        sframe["id"] =1760 + ch
        sframe["data"] = [0x01, address & 0xFF, (address & 0xFF00) >> 8, 64]
        self.__canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe["id"] == sframe["id"]+1 and \
                    rframe["data"] == sframe["data"]: break
                now = time.time()
                if now > endtime: return False
        for n in range(self.__blocksize / 8):
            print data[address + (8*n):address + (8*n) + 8]
            self.lock.acquire()
            self.__progress = float(address + 8*n) / float(self.size)
            self.lock.release()
            sframe['data'] = data[address + (8*n):address + (8*n) + 8]
            print sframe
            self.__canbus.sendFrame(sframe)
            #time.sleep(0.3)
            # TODO Need to deal with the abort from the uC somewhere
    
    def __erasePage(self, ch, address):
        sframe = {}
        sframe["id"] =1760 + ch
        sframe["data"] = [0x02, address & 0xFF, (address & 0xFF00) >> 8, 64]
        self.__canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe["id"] == sframe["id"]+1 and \
                    rframe["data"] == sframe["data"]: break
                now = time.time()
                if now > endtime: return False

    def __writePage(self, ch, address):
        sframe = {}
        sframe["id"] =1760 + ch
        sframe["data"] = [0x03, address & 0xFF, (address & 0xFF00) >> 8]
        self.__canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe["id"] == sframe["id"]+1 and \
                    rframe["data"] == sframe["data"]: break
                now = time.time()
                if now > endtime: return False

    def __sendComplete(self, ch):
        sframe = {}
        sframe["id"] =1760 + ch
        sframe["data"] = [0x05, self.__checksum & 0xFF, (self.__checksum & 0xFF00) >> 8, \
                          self.__size & 0xFF, (self.__size & 0xFF00) >> 8]
        self.__canbus.sendFrame(sframe)
        endtime = time.time() + 0.5
        while True: # Channel wait loop
            try:
                rframe = self.__canbus.recvFrame()
            except canbus.DeviceTimeout:
                pass
            else:
                if rframe["id"] == sframe["id"]+1 and \
                    rframe["data"] == sframe["data"]: break
                now = time.time()
                if now > endtime: return False

    
    def Download(self, node):
        ch = Channels()
        data = []
        while True: # Firmware load request loop
            self.__tryChannel(ch)
            # send firmware request
            if self.__tryFirmwareReq(ch, node): break
            if self.kill: exit(-1)
        # Here we are in the Firmware load mode of the node    
        # Get our firmware bytes into a normal list
        channel = ch.GetFreeChannel()
        for n in range(self.__blocks * self.__blocksize):
            data.append(self.ih[n])
        for block in range(self.__blocks):
            address = block * 64
            print "Buffer Fill at %d" % (address)
            self.lock.acquire()
            self.__currentblock = block
            self.lock.release()
            self.__fillBuffer(channel, address, data)
            # TODO Deal with timeout of above
            
            # Erase Page
            print "Erase Page Address =", address
            self.__erasePage(channel ,address)
            
            # Write Page
            print "Write Page Address =", address
            self.__writePage(channel ,address)
            
        self.__progress = 1.0
        print "Download Complete Checksum", hex(self.__checksum), "Size", self.__size
        self.__sendComplete(channel)
    
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
        
    def Connect(self):
        self.__canbus.connect()
        self.__canbus.init()
        self.__canbus.open()
        #time.sleep(3)
        #can.close()
    
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
        self.fw.Download(0xFF)
        
def config():
    parser = argparse.ArgumentParser(description='CANFIX Firmware Downloader 1.0')
    parser.add_argument('--filename', '-f', nargs=1, help='Intel Hex File to Download', required=True)
    parser.add_argument('--port', '-p', nargs=1, help='Serial Port to find CANBus interface')
    parser.add_argument('--node', '-n', type=int, nargs=1, help='CAN-FIX Node number of device')
    args = parser.parse_args()
    args = vars(args)
    output = {}
    if args['port'] != None:
        output["portname"]= args['port'][0]
    else:
        output["portname"] = ""

    output["filename"] = args['filename'][0]
    output["node"] = args['node'][0]

    return output


#***** MAIN ROUTINE *****
def main():
    args = config()
    can = canbus.Connection(args['portname'])
    
    fw = Firmware(can, args['filename'], args['node'])
    print "Program size", fw.size
    print "Block Count", fw.blocks
    
    fw.Connect()
    fwt = FirmwareThread(fw)
    fwt.start()
    
    while True:
        print fw.progress
        print "Current Block", fw.currentblock
        if not fwt.isAlive(): break
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            fw.kill = True
            exit()
       
if __name__ == '__main__':
    main()