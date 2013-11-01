#!/usr/bin/python

# An airstream server that also gets data from
#   a wiimote device.
#   Requires flWii.
# Using wiiclientsender.py and server.py is more
#   flexible since it allows the wii component to be
#   enabled and disabled separate from the airstream server.

from twisted.internet import reactor, protocol
from server import InputServiceProtocol, InputServiceFactory, DT_WIIMOUSE, DT_WII, BTN_LEFT, BTN_RIGHT
from flWii.moteDetector import MoteDetector
from flWii.mote import Mote
from flWii.leds import LedTupleFromIndex
from flWii.moteCursor import MoteMouseProcessor
from basesender import BaseSender
from GUID import getGUID
import traceback, time


# ideally:
# loop runs to check for new motes
#  callback is called when there's a new one (wii obj or id is the arg)
#  data is regularly pulled or pushed into network.

class MoteSenderInfo:
    def __init__(self, mote, deviceId, moteMouseProcessor=None):
        self.mote = mote
        self.lastPos = 0,0
        self.deviceId = deviceId
        self.moteMouseProcessor = moteMouseProcessor

class WiiSender(BaseSender):
    def __init__(self, serverObj=None, loopFreq= 200.):
        BaseSender.__init__(self)
        self.server = serverObj
        self.loopFreq = loopFreq
        self.producingInput = True
        self.motes = []
        self.connectedMoteIds = []  # moteIds
        self.moteInfo ={}
        self.moteInactivityTimeout = 60.
        self.moteDetector = None
        self.lastIdleCheckTime = time.time()
        self.idleCheckInterval = 15.0 # secs

    def sendCoordsLowBW(self, mote, moteInfo):
        moteInfo = self.moteInfo[mote.id]
        #points = mote.extractNormalizedPoints()
        point = moteInfo.moteMouseProcessor.processMouse()
        if point[0] != None:
            self.server.newDataXY(moteInfo.deviceId, point[0], point[1])
            moteInfo.lastPos = point

    def sendCoordsHighBW(self, mote, moteInfo):
        points = mote.extractNormalizedPoints()
        for point in points:
            #print "SENDING POINT:", point
            self.server.newDataXY(moteInfo.deviceId, point[0], point[1])
        if len(points):
            moteInfo.lastPos = point[-1]

    def iteration(self):
        for mote in self.motes:
            moteInfo = self.moteInfo[mote.id]
            """
            #points = mote.extractNormalizedPoints()
            point = moteInfo.moteMouseProcessor.processMouse()
            if point[0] != None:
                self.server.newDataXY(moteInfo.deviceId, point[0], point[1])
                moteInfo.lastPos = point
            """
            #self.sendCoordsHighBW(mote, moteInfo)
            self.sendCoordsLowBW(mote, moteInfo)

            buttonEvents = mote.extractButtonEvents()
            for event in buttonEvents:
                print "BUTTON:", event[0], event
                if event[1]:
                    print "pressed."
                else:
                    print "released."

                # Mouse simulation so far:
                """
                if event[0] == "a":
                    if event[1] == True: self.server.newDataButtonEvent(moteInfo.deviceId, BTN_LEFT, moteInfo.lastPos[0], moteInfo.lastPos[1])
                    elif event[1] == False: self.server.newDataButtonUpEvent(moteInfo.deviceId, BTN_LEFT, moteInfo.lastPos[0], moteInfo.lastPos[1])
                    else: print "buttonEvent: Invalid state for A button"
                elif event[0] == "b":
                    if event[1] == True: self.server.newDataButtonEvent(moteInfo.deviceId, BTN_RIGHT, moteInfo.lastPos[0], moteInfo.lastPos[1])
                    elif event[1] == False: self.server.newDataButtonUpEvent(moteInfo.deviceId, BTN_RIGHT, moteInfo.lastPos[0], moteInfo.lastPos[1])
                    else: print "buttonEvent: Invalid state for B button"
                """

                # self.server.newDataButtonEvent(moteInfo.deviceId, event[0], moteInfo.lastPos[0], moteInfo.lastPos[1])

                if event[1] == True:
                    self.server.newDataButtonEvent(moteInfo.deviceId, event[0], moteInfo.lastPos[0], moteInfo.lastPos[1])
                else:
                    self.server.newDataButtonUpEvent(moteInfo.deviceId, event[0], moteInfo.lastPos[0], moteInfo.lastPos[1])

        self.checkForIdleMotes()

    def checkForIdleMotes(self):
        if time.time() - self.lastIdleCheckTime > self.idleCheckInterval:
            self.lastIdleCheckTime = time.time()

            for mote in self.motes:
                if mote.getIdleSecs() > self.moteInactivityTimeout:
                    self.disconnectMote(mote)
                    print "Mote Timeout, Will start searching in 5 sec (to avoid auto-reconnect)"
                    reactor.callLater(5.0, self.moteDetector.reinitiateSearching)

                print mote.id, "idle Time:", mote.getIdleSecs()



    def disconnectMote(self, mote):
        if mote.id in self.connectedMoteIds:
            self.connectedMoteIds.remove(mote.id)
        if mote in self.motes:
            self.motes.remove(mote)
        mote.disconnect()

    def loop(self):
        # print "loop"
        try:
            if self.producingInput:
                self.iteration()
        except:
            traceback.print_exc()
        reactor.callLater(1.0 / self.loopFreq, self.loop)

    def newMote(self, newId, sock):
        print "newMote:", newId
        self.connectedMoteIds.append( newId )
        mote = Mote(id=newId)
        ledTuple = LedTupleFromIndex(len(self.connectedMoteIds))
        mote.connect(connectedIntSock=sock)
        self.motes.append(mote)
        #self.deviceId = self.server.registerDevice(DT_WIIMOUSE, self)
        self.deviceId = self.server.registerDevice(DT_WII, self)
        self.moteInfo[mote.id] = MoteSenderInfo(mote, self.deviceId, MoteMouseProcessor(mote))
        if mote.connected:
            mote.setLeds(*ledTuple)
            mote.startReadThread()
            mote.irBasicModeOn(changeOnly=False)

    def getAlreadyConnectedIds(self):
        return self.connectedMoteIds

    def setMoteDetector(self, moteDetector):
        self.moteDetector = moteDetector

def parseArgs():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print data")
    parser.add_option("-p", "--port",
                      action="store", dest="port", default=11000,
                      type="int", help="airstream server port")
    parser.add_option("-m", "--msgsPerSec",
                      action="store", type="float", dest="loopFreq",
                      default=100.0, help="set Looping Frequency ")
    (options, args) = parser.parse_args()
    return (options, args)


def main():

    (options, args) = parseArgs()

    factory = InputServiceFactory()
    factory.protocol = InputServiceProtocol
    reactor.listenTCP(11000,factory)

    wiiSender = WiiSender(factory, loopFreq=options.loopFreq)

    moteDetector = MoteDetector(numToConnect=1, detectedCallback=wiiSender.newMote, getAlreadyConnectedIdsCallback=wiiSender.getAlreadyConnectedIds);
    moteDetector.keepFirstConnection=True
    moteDetector.startInThread()

    wiiSender.setMoteDetector(moteDetector)

    reactor.callLater(0.0, wiiSender.loop)

    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
