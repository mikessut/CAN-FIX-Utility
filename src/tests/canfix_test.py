import canbus
import canfix

def check_equal(name, first, second, p):
    if first != second:
        print p.name, name, "not equal", first, "!=", second
        return 1
    return 0

def node_alarm_test():
    result = 0
    tests = []
    # Check every node number
    for n in range(1,255):
        f = {"frame":canbus.Frame(n, [0x01, 0x02, 1,2,3,4,5]), "node":n, "code":513, "data":[1, 2, 3, 4, 5]}
        tests.append(f)
    # Check edge conditions of error codes
    f = {"frame":canbus.Frame(n, [0x00, 0x00, 1,2,3,4,5]), "node":n, "code":0, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0xFF, 0xFF, 1,2,3,4,5]), "node":n, "code":65535, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0x00, 0xFF, 1,2,3,4,5]), "node":n, "code":65280, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0xFF, 0x00, 1,2,3,4,5]), "node":n, "code":255, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0x00, 0x01, 1,2,3,4,5]), "node":n, "code":256, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0x01, 0x00, 1,2,3,4,5]), "node":n, "code":1, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0x00, 0xFF,1,2,3,4,5]), "node":n, "code":65280, "data":[1, 2, 3, 4, 5]}
    tests.append(f)
    # Check data padding
    f = {"frame":canbus.Frame(n, [0xFF, 0xFF, 1,2]), "node":n, "code":65535, "data":[1, 2, 0, 0, 0]}
    tests.append(f)
    f = {"frame":canbus.Frame(n, [0xFF, 0xFF]), "node":n, "code":65535, "data":[0, 0, 0, 0, 0]}
    tests.append(f)
    
    for each in tests:
        p = canfix.parseFrame(each["frame"])
        if type(p) != canfix.NodeAlarm:
            result += 1
            print("Should be a Node Alarm", type(p))
        if p.node != each["node"]:
            result +=1
            print("Node does not match", p.node)
        if p.alarm != each["code"]:
            result +=1
            print("Node Error Code does not match", p.alarm)
        if p.data != each["data"]:
            result +=1
            print("Data Mismatch", p.data, "!=", each["data"])
    # Check out of bounds
    f = canbus.Frame(256, [0x00, 0xFF])
    p = canfix.parseFrame(f)
    if type(p) == canfix.NodeAlarm:
        result += 1
        print("Should not be a node alarm")
    return result
    
def parameter_test():
    result = 0
    t=[]
    # Parameter Frame [Node][Index][FCode][Data LSB][.][.][.][Data MSB]
    t.append({'frame':canbus.Frame(256, [0x01, 0x00, 0,1,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Flap Control Switches #1", 
              'value':[True] + [False]*7})
    t.append({'frame':canbus.Frame(257, [0x01, 0x00, 0,0x02,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Flap Control Switches #2", 
              'value':[False,True] + [False]*6})
    t.append({'frame':canbus.Frame(258, [0x01, 0x00, 0,1,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #1", 
              'value':[True] + [False]*15})
    t.append({'frame':canbus.Frame(259, [0x01, 0x00, 0,1,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #2", 
              'value':[True] + [False]*15})
    # Check the WORD type handling
    t.append({'frame':canbus.Frame(259, [0x01, 0x00, 0,2,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #2", 
              'value':[False, True] + [False]*14})
    t.append({'frame':canbus.Frame(259, [0x01, 0x00, 0,0x80,0,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #2", 
              'value':[False]*7+[True] + [False]*8})
    t.append({'frame':canbus.Frame(259, [0x01, 0x00, 0,0x80,0x01,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #2", 
              'value':[False]*7+[True] + [True]+[False]*7})
    t.append({'frame':canbus.Frame(259, [0x01, 0x00, 0,0x00,0x80,0,0]),'pass':True,
              'node':1, 'index':0, 'fail':False, 'qual':False, 'annunciate':False,
              'name':"Trim Switches #2", 
              'value':[False]*15+[True]})
    
    
    for each in t:
        p = canfix.parseFrame(each['frame'])
        if each['pass']==False:
            if p != None:
                result += 1
                print("Should have failed", each)
        else:
            if type(p) != canfix.Parameter:
                result += 1
                print("Should be a Parameter", type(p))
            result += check_equal('n=Node', p.node, each['node'],p)
            result += check_equal('Name', p.name, each['name'],p)
            result += check_equal('Index', p.index, each['index'],p)
            result += check_equal('Value', p.value, each['value'],p)
            #result += check_equal('index', p.index, each['index'])
            
    return result

def run_test():
    print "Test id=0 -",
    p = canfix.parseFrame(canbus.Frame(0x00,[1,2,3,4,5]))
    if p==None:
        print("[OK]")
    else:
        print("[FAIL")
    
    print "Node Alarm Tests -",
    if node_alarm_test() == 0: print("[OK]")
    else: print("[FAIL]")
    
    print "Parameter Tests -",
    if parameter_test() == 0: print("[OK]")
    else: print("[FAIL]")
    
    
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
    #    print '-'
    #    print str(f)
    #    print str(p)
    """
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
    """