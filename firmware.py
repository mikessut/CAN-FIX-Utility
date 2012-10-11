#!/usr/bin/python

from intelhex import IntelHex
import crc
import string
import time
import argparse

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


def sendCommand(str):
    ser.write(str)
    result = readResponse()
    while 1:
        if result == "z\r":
            return True
        elif result == "\x07":
            return False
        return



def config():
    parser = argparse.ArgumentParser(description='CANFIX Firmware Downloader 1.0')
    parser.add_argument('--filename', '-f', nargs=1, help='Intel Hex File to Download')
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
    ih = IntelHex(args['filename'])

    print "Calculating Checksum for file", args['filename']
    cs = crc.crc16()
    for each in range(ih.minaddr(), ih.maxaddr()+1):
        cs.addByte(ih[each])

    print "Program Size ", ih.maxaddr()+1
    print "Checksum ", hex(cs.getResult())



    commands = ["t7015f60701f700\r",
            "t7015f60701f701\r",
            "t7015f60701f702\r",
            "t7015f60701f703\r",
            "t7015f60701f704\r",
            "t7015f60701f705\r",            
            "t7015ff0701f700\r",
            "t6e0401000000\r",
            "t6e03020000\r",
            "t6e03030000\r",
            "t6e0104\r",
            "t6e040500000000\r"]



    for each in commands:
        sendCommand(each)
        result = readResponse()
        if result == -1:
            print "Timeout Continue"
        else:
            print result

    ser.close

if __name__ == '__main__':
    main()