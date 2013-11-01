import mpi
import time
from flWii.connectToMote import connectToMote
from flWii.moteCursor import MoteMouse
from tileMote import TileMote
from mouseUpdater import WiiMouseUpdater

def SetupMoteControl(cursor, app, displayWidth, displayHeight, moteId="00:17:AB:32:BF:EF", leds=(1,0,0,0), configUI=None, renderers = None, masterObjects=None, cursorListList=None, moteManager=None):
    tileMote = TileMote(cursor, displayWidth, displayHeight)
    if mpi.rank == 0:
        mote = connectToMote(moteId, leds, changeOnly=True)
        print "Setting up MoteMouse"
        moteMouse = MoteMouse(mote,tileMote)
    else:
        moteMouse = None
        mote = None

    app.addDynamicObject(WiiMouseUpdater(moteMouse, tileMote, configUI=configUI, renderers=renderers, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=moteManager), addToRenderer=False)

    return mote, moteMouse, tileMote

class MoteManager: # FIXME prototype, move to separate file next
    def __init__(self, app, fullRect, masterCursors, configUI=None, renderers = None, masterObjects=None, cursorListList=None):
        mote, moteMouse, tileMote = SetupMoteControl(masterCursors[0], app, fullRect.width, fullRect.height, moteId=None, leds=(1,0,0,0),renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=self)
        mote2, moteMouse2, tileMote2 = SetupMoteControl(masterCursors[1], app, fullRect.width, fullRect.height, moteId=None, leds=(0,1,0,0),renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=self)
        mote3, moteMouse3, tileMote3 = SetupMoteControl(masterCursors[2], app, fullRect.width, fullRect.height, moteId=None, leds=(0,0,1,0),renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=self)
        mote4, moteMouse4, tileMote4 = SetupMoteControl(masterCursors[3], app, fullRect.width, fullRect.height, moteId=None, leds=(0,0,0,1),renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=self)

        self.connectedMoteDict = {}  # moteId: mote
        self.motes = [mote, mote2, mote3, mote4]
        self.moteMice = [moteMouse, moteMouse2, moteMouse3, moteMouse4]
        #self.tileMotes = [tileMote, tileMote2, tileMote3, tileMote4]
        self.disconnectedMoteIndexes = [0,1,2,3]
        self.moteDetector = None # should be set after it's created.
        self.idleTimeoutSecs = 60. # 5 * 60.
        self.idleCheckInterval =  15. # secs
        self.lastIdleCheckTime = time.time()

    def newMoteDetected(self, moteId):
        if len(self.disconnectedMoteIndexes) > 0:
            moteIndex = self.disconnectedMoteIndexes.pop(0)
            print "new mote detected:", moteId, moteIndex
            mote = self.motes[moteIndex]
            moteMouse = self.moteMice[moteIndex]
            #tileMote = self.tileMotes[moteIndex]
            mote.id = moteId
            self.connectedMoteDict[moteId] = moteIndex
            try:
                mote.connect()
                mote.setLeds(moteIndex==0, moteIndex==1, moteIndex==2, moteIndex==3)
                if mote.readThread == None:
                    mote.startReadThread()
                mote.irBasicModeOn(changeOnly=True)
                moteMouse.mote = mote
            except MoteConnectFailed:
                print "Mote Connect failed."

    def disconnectMote(self, moteId):
        if moteId in self.connectedMoteDict:
            moteIndex = self.connectedMoteDict[moteId]
            mote = self.motes[moteIndex]
            self.moteMice[moteIndex].moteMouse = None
            mote.disconnect()
            self.disconnectedMoteIndexes.insert(0, moteIndex)
            del self.connectedMoteDict[moteId] # marked as not connected, so connection attempts will start now.
        else:
            print "warning: disconnecting mote that wasn't connected."

    def getAlreadyConnectedIds(self):
        return self.connectedMoteDict.keys()

    def setMoteDetector(self, d):
        self.moteDetector = d

    def update(self, secs, app):
        if time.time() - self.lastIdleCheckTime > self.idleCheckInterval:
            self.lastIdleCheckTime = time.time()
            for moteId, moteIndex in self.connectedMoteDict.items():
                if self.moteMice[moteIndex].mote.getIdleSecs() > self.idleTimeoutSecs:
                    self.disconnectMote(moteId)
                    print "Mote Timeout, Will start searching in 5 sec (to avoid auto-reconnect)"
                    app.callLater(5.0, self.moteDetector.reinitiateSearching, [])
                print moteId, "idle Time:", self.moteMice[moteIndex].mote.getIdleSecs()

    def incrementNumMotes(self, numToAdd):
        num = (self.moteDetector.numToConnect + numToAdd) % 5
        if num == 0:
            num += 1
        self.moteDetector.numToConnect = num
        print "Total Wiimotes to be connected:", self.moteDetector.numToConnect

        if self.moteDetector.numToConnect > len(self.getAlreadyConnectedIds()):
            self.moteDetector.reinitiateSearching()
