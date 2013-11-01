import sys
import time
import bluetooth
import threading
import binascii
import traceback
from bluetooth import BluetoothSocket, L2CAP, BluetoothError
from threading import Lock

class MoteConnectFailed(Exception):
    pass

def dectobin(number):
    if number < 1: return ""
    else:return dectobin(number/2) + str(number & 1)

def detectAllPossible():
    print "performing inquiry..."
    nearbyDevices = bluetooth.discover_devices(lookup_names = False)
    print "Devices found: %s" % len(nearbyDevices)
    return nearbyDevices

def detectMotes():
    print "performing inquiry..."

    nearbyDevices = bluetooth.discover_devices(lookup_names = True)
    print "Devices found: %s" % len(nearbyDevices)
    print "Devices:", nearbyDevices

    motes=[]
    for device in nearbyDevices:
        if device[1] and "Nintendo" in device[1]:
            motes.append(device)
            print "Wiimote: ", device[1], device[0]
    return motes

def getServices(deviceId):
    print "Finding services for", deviceId, "..."
    services = bluetooth.find_service(address=deviceId)
    return services

class Mote:
    INTERRUPT_PORT = 19
    CONTROL_PORT = 17

    def __init__(self, id=None, name=""): 
        self.id = id 
        self.name = name
        self.connected = False
        self.irMode = None
        self.reportMode = None
        self.dataLock = Lock()
        self.dataPoints = []
        self.dataPointsAndSize = []
        self.dataPointsFull = []
        self.dataPointsFullFirstPart = []
        self.buttonEvents = []
        # A,B,1,2,Home,Plus,Minus,Left,Right,Up,Down
        self.buttonState = {"a":bool(0),
                            "b":bool(0),
                             1:bool(0),
                             2:bool(0),
                            "h":bool(0),
                            "p":bool(0),
                            "m":bool(0),
                            "l":bool(0),
                            "r":bool(0),
                            "u":bool(0),
                            "d":bool(0)}
        self.readThread = None
        self.idleStartTime = time.time()
        self.idleLastPoint = (0.0,0.0)

    def getIdleSecs(self):
        return time.time() - self.idleStartTime

    def restartIdleTime(self):
        self.idleStartTime = time.time()

    def isIrModeFull(self):
        #if self.reportMode == 0x3e or self.reportMode == 0x3f:
        if self.irMode == "f":
            return True
        else:
            return False

    def isIrModeExt(self):
        #if self.reportMode == 0x33:
        if self.irMode == "e":
            return True
        else:
            return False

    def isIrModeBasic(self):
        #if self.reportMode == 0x36 or self.reportMode == 0x37:
        if self.irMode == "b":
            return True
        else:
            return False

    def getServices(self):
        return getServices(self.id)

    def connect(self, connectedIntSock=None):
        self.restartIdleTime()
        try:
            if not self.id:  # == None or == 0
                print "note: skipping connect in mote.connect, id not valid."
                return

            if connectedIntSock:
                self.intSock = connectedIntSock
            else:
                self.intSock = BluetoothSocket(L2CAP)
                self.intSock.connect( (self.id, self.INTERRUPT_PORT) )
            self.ctrlSock = BluetoothSocket(L2CAP)
            self.ctrlSock.connect( (self.id, self.CONTROL_PORT) )
            if self.ctrlSock and self.intSock:
                print "Connected to", self.id
                self.connected = True
        except bluetooth.BluetoothError, e:
            if e.message=="time out": 
                print "Timed out when connected to mote."          
                raise MoteConnectFailed()
            else:
                raise


    def disconnect(self):
        self.connected = False
        self.intSock.close()
        self.ctrlSock.close()
        print "Disconnected from ", self.id

    def sendCmd(self, cmd):
      fs = ''
      for b in cmd:
          fs += str(b).encode("hex").upper()  + " "
      print "sending ", str(len (cmd)), "bytes:", fs
      self.ctrlSock.send( cmd )
      time.sleep(0.001)

    def rumbleOn(self):
        self.sendCmd("\x52\x13\x01")

    def rumbleOff(self):
        self.sendCmd("\x52\x13\x00")

    def setLeds(self, led1=0, led2=0, led3=0, led4=0):
        value = led1 + 2 * led2 +  4 * led3 + 8 * led4
        valueHexStr = binascii.unhexlify("%X0" % value)
        self.sendCmd("\x52\x11" + valueHexStr )

    def setLedsOff(self):
        self.sendCmd("\x52\x11\x00")

    # Modes:
    # 0x30 just buttons
    # 0x31 motion sensor
    # 0x32 ir camera
    # 0x33 ir camera and motion sensor

    def motionModeOn(self, changeOnly=False): # change only has little effect
        if changeOnly:
            self.sendCmd("\x52\x12\x04\x31")
        else:
            self.sendCmd("\x52\x12\x00\x31")

    def motionModeOff(self):
        self.allMotionOff()

    def allMotionOff(self):
        self.sendCmd("\x52\x12\x00\x30")

    def writeControlRegister(self, offset, size, data):
        # 52 16 MM FF FF FF SS DD DD DD ... DD
        # offset is 3 bytes, size is 1 byte, data is up to 16 bytes
        if len(data) < 16:  # pad out to 16 bytes
            data = data + "\x00" * (16 - len(data))
        self.sendCmd("\x52\x16\x04" + offset + size + data)

    def irBasicModeOn(self, changeOnly=False):
        self._irOn(changeOnly, mode="b");

    def irExtendedModeOn(self, changeOnly=False):
        self._irOn(changeOnly, mode="e");

    def irFullModeOn(self, changeOnly=False):
        self._irOn(changeOnly, mode="f");

    def _irOn(self, changeOnly=False, mode="b"):
        self.irMode = mode
        # mode can be ("b")asic, ("e")xtended, ("f")ull

        #Turn on IR, part 1
        self.sendCmd("\x52\x13\x04")
        time.sleep(0.1)
        #Turn on IR, part 2
        self.sendCmd("\x52\x1A\x04")
        time.sleep(0.1)

        # Start config
        self.writeControlRegister("\xb0\x00\x30", "\x01", "\x08")
        time.sleep(0.1)

        """
        # write sensitity part 1
        self.writeControlRegister("\xb0\x00\x00", "\x09", "\x02\x00\x00\x71\x01\x00\xaa\x00\x64")
        time.sleep(0.1)
        # write sensitity part 2
        self.writeControlRegister("\xb0\x00\x1a", "\x02", "\x63\x03")
        time.sleep(0.1)
        """
        # write sensitity part 1
        self.writeControlRegister("\xb0\x00\x00", "\x09", "\x00\x00\x00\x00\x00\x00\x90\x00\x41")
        time.sleep(0.1)
        # write sensitity part 2
        self.writeControlRegister("\xb0\x00\x1a", "\x02", "\x40\x00")
        time.sleep(0.1)

        # Mode number, 1, 3, or 5
        if mode == "e":
            self.writeControlRegister("\xb0\x00\x33", "\x01", "\x03")
        elif mode == "f":
            self.writeControlRegister("\xb0\x00\x33", "\x01", "\x05")
        else: # if mode == "b": # default to basic
            self.writeControlRegister("\xb0\x00\x33", "\x01", "\x01")
        time.sleep(0.1)

        # Finish config
        self.writeControlRegister("\xb0\x00\x30", "\x01", "\x08")
        time.sleep(0.1)

        # print "Sending read cmd"
        # self.sendCmd("\x52\x17\x04\xB0\x00\x00\x00\x33")  # read from ir
        # time.sleep(0.1)

        # Enable reporting
        if mode == "e": # extended
            if changeOnly:
                self.sendCmd("\x52\x12\x00\x33")   # 33, (19)Btns, 3 A, 12 IR
            else:
                self.sendCmd("\x52\x12\x04\x33")   # 33, (19)Btns, 3 A, 12 IR
            self.reportMode = 0x33
        elif mode == "f": # full
            if changeOnly:
                self.sendCmd("\x52\x12\x00\x3e")   # 3e, (23)Btns, 3 A, 36 IR 
            else:                                  # 3f, (23)Btns, 3 A, 36 IR
                self.sendCmd("\x52\x12\x04\x3e")
            self.reportMode = 0x3e
        else:            # basic
            if changeOnly:
                self.sendCmd("\x52\x12\x00\x36")   # 36, (23)Btns, 3 A, 10 IR, 9 ext
                # self.sendCmd("\x52\x12\x00\x37") # 37, (23)Btns, 3 A, 10 IR, 9 ext
            else:
                self.sendCmd("\x52\x12\x04\x36")   # 36, (23)Btns, 3 A, 10 IR, 9 ext
            self.reportMode = 0x36

    def irModeOff(self):
        self.allMotionOff()

    def irAndMotionModeOn(self, changeOnly=False):
        if changeOnly:
            self.sendCmd("\x52\x12\x04\x33")
        else:
            self.sendCmd("\x52\x12\x00\x33")

    def irAndMotionModeOff(self):
        self.allMotionOff()

    def extractNormalizedPoints(self, deletePoints=True):
        normalizedList = []
        points = self.extractPoints(deletePoints)
        if len(points) > 0:
            # print "extract points3 returned:", points
            for plist in points:
                tmp = [] 
                for pt in plist:
                    tmp.append( (pt[0] / 1023., pt[1] / 767.) )
                normalizedList.append(tmp)
        # print "extract points4 (norm) returning:", normalizedList
        return normalizedList

    def extractLastNormalizedPoint(self, deletePoints=True):
        pt = self.extractLastPoint(deletePoints)
        if pt != None: 
            return ( (pt[0] / 1023., pt[1] / 767.) )
        else:
            return None

    def extractPoints(self, deletePoints=True):
        tmp = []
        self.dataLock.acquire() 
        try:
            if deletePoints:
                tmp = self.dataPoints
                self.dataPoints = []
            else:
                tmp = list(self.dataPoints)
        except:
            traceback.print_exc()
        finally:
            self.dataLock.release()
        return tmp

    def extractLastPoint(self, deletePoints=True):
        tmp = None
        self.dataLock.acquire() 
        #print "extractLastPoint:", self.dataPoints
        try:
            if deletePoints:
                if len(self.dataPoints) > 0:
                    if len(self.dataPoints[-1]) > 0:
                        tmp = self.dataPoints[-1][-1]
                        self.dataPoints = []
            else:
                if len(self.dataPoints) > 0:
                    if len(self.dataPoints[-1]) > 0:
                        tmp = copy.copy(self.dataPoints[-1][-1])
        except:
            traceback.print_exc()
        finally:
            self.dataLock.release()
        print "extractLastPoint: pt: ", tmp
        return tmp

    def extractNormalizedPointsAndSize(self, deletePoints=True):
        normalizedList = []
        points = self.extractPointsAndSize(deletePoints)
        if len(points) > 0:
            # print "extract points3 returned:", points
            for plist in points:
                tmp = [] 
                for pt in plist:
                    tmp.append( (pt[0] / 1023., pt[1] / 767., pt[2] / 15.) )
                normalizedList.append(tmp)
        # print "extract points4 (norm) returning:", normalizedList
        return normalizedList

    def extractPointsAndSize(self, deletePoints=True):
        tmp = []
        self.dataLock.acquire() 
        try:
            if deletePoints:
                tmp = self.dataPointsAndSize
                self.dataPointsAndSize = []
            else:
                tmp = list(self.dataPointsAndSize)
        except:
            traceback.print_exc()
        finally:
            self.dataLock.release()
        return tmp

    def extractButtonEvents(self, deleteEvents=True):
        tmp = []
        self.dataLock.acquire() 
        try:
            if deleteEvents:
                tmp = self.buttonEvents
                self.buttonEvents = []
            else:
                tmp = list(self.buttonEvents)
        except:
            traceback.print_exc()
        finally:
            self.dataLock.release()
        return tmp

    def storeButtons(self, data):
        vals = [ord(d) for d in data]
        # Assume all are off to start
        #print vals
        a = bool(vals[1] & 0x08)
        b = bool(vals[1] & 0x04)
        one = bool(vals[1] & 0x02)
        two = bool(vals[1] & 0x01)
        home = bool(vals[1] & 0x80)
        left = bool(vals[0] & 0x01)
        right = bool(vals[0] & 0x02)
        down = bool(vals[0] & 0x04)
        up = bool(vals[0] & 0x08)
        plus = bool(vals[0] & 0x10)
        minus = bool(vals[1] & 0x10)
        #print "A:%s B:%s 1:%s 2:%s Home:%s Plus:%s Minus:%s Left:%s Right:%s Up:%s Down:%s" %(a,b,one,two,home,plus,minus,left,right,up,down)
        if self.buttonState["a"] != a:
            self.buttonState["a"] = a
            self.buttonEvents.append( ("a", a) )
        if self.buttonState["b"] != b:
            self.buttonState["b"] = b
            self.buttonEvents.append( ("b", b) )
        if self.buttonState[1] != one:
            self.buttonState[1] = one
            self.buttonEvents.append( (1, one) )
        if self.buttonState[2] != two:
            self.buttonState[2] = two
            self.buttonEvents.append( (2, two) )
        if self.buttonState["h"] != home:
            self.buttonState["h"] = home
            self.buttonEvents.append( ("h", home) )
        if self.buttonState["p"] != plus:
            self.buttonState["p"] = plus
            self.buttonEvents.append( ("p", plus) )
        if self.buttonState["m"] != minus:
            self.buttonState["m"] = minus
            self.buttonEvents.append( ("m", minus) )
        if self.buttonState["l"] != left:
            self.buttonState["l"] = left
            self.buttonEvents.append( ("l", left) )
        if self.buttonState["r"] != right:
            self.buttonState["r"] = right
            self.buttonEvents.append( ("r", right) )
        if self.buttonState["u"] != up:
            self.buttonState["u"] = up
            self.buttonEvents.append( ("u", up) )
        if self.buttonState["d"] != down:
            self.buttonState["d"] = down
            self.buttonEvents.append( ("d", down) )

        if len(self.buttonEvents) > 0:
            self.restartIdleTime()

    def storePoints(self, points):
        # print "pointsReceived: ", points
        self.dataLock.acquire() 
        try:
            self.dataPoints.append(points)
        except:
            traceback.print_exc()
            self.dataLock.release()

        if len(points) > 0:
            for p in points:
                if p != self.idleLastPoint:
                    self.restartIdleTime()
                    break
            self.idleLastPoint = points[-1]

        self.dataLock.release()

    def storePointsAndSize(self, points):
        # print "pointsReceived: ", points
        self.dataLock.acquire() 
        try:
            self.dataPointsAndSize.append(points)
        except:
            traceback.print_exc()
            self.dataLock.release()
        self.dataLock.release()

    def extractNormalizedPointsFull(self, deletePoints=True):
        normalizedList = []
        points = self.extractPointsFull(deletePoints)
        if len(points) > 0:
            # print "extract points3 returned:", points
            for plist in points:
                tmp = [] 
                for pt in plist:
                    tmp.append( (pt[0] / 1023., pt[1] / 767., pt[2] / 15., pt[3] / 127., pt[4] /   95., pt[5] / 127., pt[6] /   95., pt[7] / 255. ) )
                normalizedList.append(tmp)
        # print "extract points4 (norm) returning:", normalizedList
        return normalizedList

    def extractPointsFull(self, deletePoints=True):
        tmp = []
        self.dataLock.acquire() 
        try:
            if deletePoints:
                tmp = self.dataPointsFull
                self.dataPointsFull = []
            else:
                tmp = list(self.dataPointsFull)
        except:
            traceback.print_exc()
        finally:
            self.dataLock.release()
        return tmp

    def storePointsFull(self, points, firstPart):
        if firstPart == True:
            self.dataPointsFullFirstPart = points
            return
        # print "pointsReceived: ", points
        self.dataLock.acquire() 
        try:
            self.dataPointsFull.append(self.dataPointsFullFirstPart + points)
            self.dataPointsFullFirstPart = []
        except:
            traceback.print_exc()
            self.dataLock.release()
        self.dataLock.release()

    def readDataLoop(self):
        self.intSock.settimeout(0.1)
        while self.connected:
            # print "readDataIteration"
            try:
                data = self.intSock.recv(23)
                if len(data):
                    if self.reportMode == 0x36 and len(data) > 22: # basic mode
                        # (a1) 36 BB BB II II II II II II II II II II EE EE EE EE EE EE EE EE EE
                        #print "IR:", [ord(d) for d in data[4:14]]
                        vals = [ord(d) for d in data[4:14]]
                        # X1<7:0> Y1<7:0> | Y1<9:8> X1<9:8> Y2<9:8> X2<9:8> | x2<7:0 Y2<7:0>
                        # print "vals[0:5]", vals[0:5], [255,255,255,255,255], vals[0:4] != [255,255,255,255,255]
                        #initialX = -511
                        #initialY = -383
                        if vals[0:5] != [255,255,255,255,255]:
                            x1 = vals[0] + ((vals[2] & 0x30) << 4);
                            y1 = vals[1] + ((vals[2] & 0xC0) << 2);
                            x2 = vals[3] + ((vals[2] & 0x03) << 8);
                            y2 = vals[4] + ((vals[2] & 0x0C) << 6);
                            # print "Extras: ", vals[0], (vals[2] & 0x30), (vals[2] & 0x30) << 4, vals[0] + (vals[2] & 0x30) << 4, vals[0] + ((vals[2] & 0x30) << 4)
                            # print "read points:", x1, y1, ", ", x2, y2
                        else:
                            x1 = 0; y1 = 0; x2 = 0; y2 = 0;
                            # x1 = initialX; y1 = initialY; x2 = initialX; y2 = initialY;

                        if vals[5:10] != [255,255,255,255,255]:
                            x3 = vals[5] + ((vals[7] & 0x30) << 4);
                            y3 = vals[6] + ((vals[7] & 0xC0) << 2);
                            x4 = vals[8] + ((vals[7] & 0x03) << 8);
                            y4 = vals[9] + ((vals[7] & 0x0C) << 6);
                        else:
                            x3 = 0; y3 = 0; x4 = 0; y4 = 0;
                            # x3 = initialX; y3 = initialY; x4 = initialX; y4 = initialY;
                        self.storeButtons(data[2:4])
                        self.storePoints( [(x1,y1), (x2,y2), (x3,y3), (x4,y4) ] )
                    elif self.reportMode == 0x33:
                        # (a1) 36 BB BB II II II II II II II II II II EE EE EE EE EE EE EE EE EE
                        vals = [ord(d) for d in data[7:19]]
                        results = []
                        for i in range(4):
                            #results.append(
                            #  ( (vals[i*3+0] << 2) + ((vals[i*3+2] & 0x30) >> 2), # x
                            #   (vals[i*3+1] << 2) + ((vals[i*3+2] & 0xC0) >> 4), # y
                            #   vals[i*3+2] & 0x15)                        # size
                            #)
                            results.append(
                              (vals[i*3+0] + ((vals[i*3+2] & 0x30) << 4), # x
                               vals[i*3+1] + ((vals[i*3+2] & 0xC0) << 2), # y
                               vals[i*3+2] & 0x15)                        # size
                            )

                        # print "results: ", results
                        self.storeButtons(data[2:4])
                        self.storePointsAndSize(results)

                    elif self.reportMode == 0x3e:
                        # (a1) 3e BB BB AA II II II II II II II II II II II II II II II II II II
                        results = []
                        vals = [ord(d) for d in data[5:23]]
                        for i in range(2):
                            results.append(
                              (vals[i*9+0] + ((vals[i*9+2] & 0x30) << 4), # x
                               vals[i*9+1] + ((vals[i*9+2] & 0xC0) << 2), # y
                               vals[i*9+2] & 0x15,                       # size
                               vals[i*9+3] & 0x7F,    # xmin
                               vals[i*9+4] & 0x7F,    # ymin
                               vals[i*9+5] & 0x7F,    # xmax
                               vals[i*9+6] & 0x7F,    # ymax
                               vals[i*9+8] )          # intensity
                            )
                        self.storeButtons(data[2:4])
                        if ord(data[1]) == 0x3e:
                            self.storePointsFull(results, firstPart=True)
                        else:
                            self.storePointsFull(results, firstPart=False)

                    else:
                        print "Received: " + binascii.hexlify(data)
            except BluetoothError:
                pass
            #time.sleep(0.001)
        print "No longer connected.  ReadDataLoop exiting."
        self.readThread = None

    def startReadThread(self):
        self.readThread = threading.Thread(target=self.readDataLoop)
        self.readThread.start()
 
# pos info
# A) position
# B) position and size
# C) position, size, and pixel value
# camera bit rate: 400 kbaud


