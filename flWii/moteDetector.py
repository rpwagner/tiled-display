
import bluetooth
import select
import time

import threading
from moteCache import MoteCache


class SimpleDiscoverer(bluetooth.DeviceDiscoverer):

    def __init__(self):
        bluetooth.DeviceDiscoverer.__init__(self)
        
    
    def pre_inquiry(self):
        self.done = False
    
    def device_discovered(self, address, device_class, name):
        # print "%s - %s" % (address, name)
        self.discoverCallback(address, device_class, name)
        return
        
        # get some information out of the device class and display it.
        # voodoo magic specified at:
        #
        # https://www.bluetooth.org/foundry/assignnumb/document/baseband
        major_classes = ( "Miscellaneous", 
                          "Computer", 
                          "Phone", 
                          "LAN/Network Access point", 
                          "Audio/Video", 
                          "Peripheral", 
                          "Imaging" )
        major_class = (device_class >> 8) & 0xf
        if major_class < 7:
            print "  %s" % major_classes[major_class]
        else:
            print "  Uncategorized"

        print "  services:"
        service_classes = ( (16, "positioning"), 
                            (17, "networking"), 
                            (18, "rendering"), 
                            (19, "capturing"),
                            (20, "object transfer"), 
                            (21, "audio"), 
                            (22, "telephony"), 
                            (23, "information"))

        for bitpos, classname in service_classes:
            if device_class & (1 << (bitpos-1)):
                print "    %s" % classname

    def inquiry_complete(self):
        self.done = True


class MoteDetector(): # just uses the simple class above from a bluetooth example.
    def __init__(self, detectedCallback, getAlreadyConnectedIdsCallback, numToConnect=1):
        self.detectedCallback = detectedCallback
        self.getAlreadyConnectedIdsCallback = getAlreadyConnectedIdsCallback
        self.discoverThread = None

        self.d = None
        self.knownBTIds = []

        moteCache = MoteCache()
        moteCache.read()
        self.knownMoteIds = moteCache.getMotes()
        if len(self.knownMoteIds) == 0:
            print "********** WARNING: not mote cache detected, no motes will be found this way."
        #self.knownMoteIds = {"00:1E:A9:4F:59:8E":""}
        self.shortCheckDelay=3.0
        self.allConnectedDelay=3.0
        self.shortTimeout = 2.0
        self.numToConnect = numToConnect

        self.searchEvent = threading.Event() # signals when to start looking for more motes

        self.keepFirstConnection=False

    def discoverIteration(self):
        rfds = select.select( self.readfiles, [], [] )[0]

        if self.d in rfds:
            self.d.process_event()

        return self.d.done

    def readyForLongCheck(self):
        return False

    def readyForShortCheck(self):
        return True

    def discoverCallback(self, address, device_class, name):
        connectedMoteIds = self.getAlreadyConnectedIdsCallback()
        if address not in connectedMoteIds and address not in self.knownBTIds:
            print "DISCOVER CALLBACK:", address, device_class, name
            if type(name) == type(""):
                if "nintendo" in name.lower():
                    self.detectedCallback(address, device_class, name)
            else:
                print "WARNING: NEED to request NAME (for never used motes)"
            self.knownBTIds.append(address)

    def tryKnownIds(self):
        connectedMoteIds = self.getAlreadyConnectedIdsCallback()
        for moteId in self.knownMoteIds.keys():
            if moteId not in connectedMoteIds:
                try:
                    print "trying to connect to known mote id:", moteId
                    INTERRUPT_PORT = 19
                    tmpIntSock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
                    tmpIntSock.settimeout(self.shortTimeout)
                    tmpIntSock.connect( (moteId, INTERRUPT_PORT) )
                    if self.keepFirstConnection:
                        self.detectedCallback(moteId, tmpIntSock)
                        tmpIntSock = 0
                    else:
                        tmpIntSock.close() # succeeded
                        #self.detectedCallback(moteId, None, None)
                        self.detectedCallback(moteId)
                except bluetooth.BluetoothError, e:
                    if e.message == "timed out":
                        print "timed out"
                    else:
                        print "Err no.:", e.errno, "Error msg:", e.message
                    try:
                        tmpIntSock.close() # succeeded
                    except Exception, e:
                        print "Error trying to close socket with failed connection.  Err no.:", e.errno, "Error msg:", e.message
            time.sleep(0.001)

    def discoverLoop(self):
        print "DISCOVERLOOOP"
        if self.readyForShortCheck():
            self.tryKnownIds()

        if self.readyForLongCheck():
            while self.readyForLongCheck():
                if self.readyForShortCheck():
                    self.tryKnownIds()
                self.d = SimpleDiscoverer() 
                self.d.discoverCallback = self.discoverCallback
                while 1:
                    #self.d.find_devices(lookup_names = True)
                    self.d.find_devices(lookup_names = False)
                    self.readfiles = [ self.d, ]
    
                    done = False
                    while done == False:
                        done = self.discoverIteration()
        else:
            print "DISCOVERLOOOP_B"
            while 1:
                try:
                    connectedMoteIds = self.getAlreadyConnectedIdsCallback()
                    print "DISCOVERLOOOP_C", len(connectedMoteIds), self.numToConnect
                    if len(connectedMoteIds) < self.numToConnect:
                        print "DISCOVERLOOOP_D", len(connectedMoteIds), self.numToConnect
                        self.tryKnownIds()
                        time.sleep(self.shortCheckDelay)
                        connectedMoteIds = self.getAlreadyConnectedIdsCallback()
                    else:
                        #time.sleep(self.allConnectedDelay)
                        print "searchEvent wait"
                        self.searchEvent.wait()
                        print "searchEvent finished waiting"
                except:
                    traceback.print_exc()

    def reinitiateSearching(self):
        self.searchEvent.set()   # calling set and clear will wake the discoverLoop
        self.searchEvent.clear()
               

    def startInThread(self):
        self.discoverThread = threading.Thread(target=self.discoverLoop)
        self.discoverThread.start()

    def startWithoutThread(self):
        self.discoverLoop()

if __name__ == "__main__":
    from connectToMote import connectToMote

    class NewMoteHandler:
        def __init__(self):
            self.motes = {}

        def handleNewMoteCallback(self, address, device_class, name):
            if address not in self.motes.keys():
                self.connectToMote(address)

        def connectToMote(self, moteId):
            mote = connectToMote(moteId)
            if mote.connected:
                self.motes[moteId] = mote

        def getConnectedMoteIds(self):
            return self.motes.keys()

    moteHandler = NewMoteHandler()
        
    detector = MoteDetector(detectedCallback=moteHandler.handleNewMoteCallback, getAlreadyConnectedIdsCallback=moteHandler.getConnectedMoteIds, numToConnect=1)
    detector.startInThread()
    
    count = 0
    import time
    numPoints = 0
    startTime = time.time()
    reportInterval = 0.5
    lastReport = startTime
    while 1:
        for moteId, mote in moteHandler.motes.items(): 
            #print "mote:", moteId, mote.extractNormalizedPoints()
            numPoints += len(mote.extractNormalizedPoints())
            #print "Numpoints:", numPoints
            currentTime = time.time()
            elapsedTime = currentTime - lastReport
            if elapsedTime > reportInterval:
                print "pts/sec:", numPoints / elapsedTime
                numPoints = 0
                lastReport = currentTime

