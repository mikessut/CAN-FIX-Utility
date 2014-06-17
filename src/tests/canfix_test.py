import canbus
import canfix

def run_test():
    frames = []
    frames.append(canbus.Frame(0x023, [0x01, 0x02, 1,2,3,4,5]))
    frames.append(canbus.Frame(0x183, [2, 0, 0, 44, 5]))
    frames.append(canbus.Frame(0x183, [2, 0, 0x10, 0, 0]))
    frames.append(canbus.Frame(0x183, [2, 0, 0x20, 0xD0, 0x7]))
    frames.append(canbus.Frame(0x183, [2, 0, 0x30, 44, 2]))
    frames.append(canbus.Frame(0x183, [2, 0, 0x30, 44]))
    frames.append(canbus.Frame(0x184, [2, 0, 0, 0xd0, 0x7, 0, 0]))
    frames.append(canbus.Frame(0x184, [2, 0, 0, 0xff, 0xff, 255, 255]))
    frames.append(canbus.Frame(0x102, [3, 0, 0, 0x55, 0xAA]))
    frames.append(canbus.Frame(0x10E, [3, 1, 0, 0x02]))
    frames.append(canbus.Frame(0x587, [1, 0, 0, ord('7'), ord('2'), ord('7'), ord('W'), ord('B')]))
    frames.append(canbus.Frame(0x4DC, [4, 0, 0, 1, 2, 0, 0]))
    frames.append(canbus.Frame(0x580, [5, 0, 0, 0x07, 4, 26]))
    frames.append(canbus.Frame(0x581, [5, 0, 0, 0xdd, 0x07, 4, 26]))
    frames.append(canbus.Frame(1795, [5, 3, 1, 2, 3]))
    frames.append(canbus.Frame(1773, [1, 2, 3, 4, 5]))
    for f in frames:
        p = canfix.parseFrame(f)
        print '-'
        print str(f)
        print str(p)
    
    na = canfix.NodeAlarm()
    na.node = 4
    na.alarm = 0x2345
    na.data = [1, 2, 3, 4]
    print na
    print na.frame
    
    p = canfix.Parameter()
    #p.identifier = 0x1
    #print p.name
    
    p.name = "indicated Airspeed"
    p.value = 132.4
    p.node = 12
    print p
    print p.getFrame()
    
    p.name = "time"
    p.value = [1,2,3]
    p.node = 13
    print p
    print p.getFrame()
    
    p.name = "date"
    p.value = [2014,2,3]
    p.node = 14
    print p
    print p.getFrame()
    
    p.name = "Aircraft Identifier"
    p.value = ['7', '2', '7', 'W', 'B']
    p.node = 15
    print p
    print p.getFrame()
    
    tw = canfix.TwoWayMsg()
    tw.channel = 0
    tw.data = [9, 10, 11, 12, 13, 14, 15, 16]
    print tw
    print tw.frame