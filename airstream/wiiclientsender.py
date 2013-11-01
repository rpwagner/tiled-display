#!/usr/bin/python

# Send data to airstream server from a
#   wii device.
#   Requires flWii.

from twisted.internet import reactor, protocol
from server import DT_WIIMOUSE, DT_WII, MT_XY, BTN_LEFT, BTN_RIGHT, MT_DONTSENDDATA, MT_BUTTONDOWN, MT_BUTTONUP
from twisted.protocols.basic import Int16StringReceiver
from wiiserver import WiiSender
from flWii.moteDetector import MoteDetector
from GUID import getGUID
import traceback, time

class WiiSenderClientProtocol(Int16StringReceiver):
    def connectionMade(self):
        try:
            print "connection made"
            # Send a msg that we don't want to receive input data.
            # deviceType, deviceIndex, msgType)
            data = "%s,%s,%s" % (DT_WII, -1, MT_DONTSENDDATA)
            self.sendString(data)
        except:
            traceback.print_exc()
     
        self.doLoop=True
        #self.loopFreq = 30.0  # leave setting in factory for now
        self.producingInput = True
        reactor.callLater(0.0, self.loop)
        self.startTime = 0.0
        self.iterationCount = 0
        self.wiiSender = None  # should be overridden in the next call
        self.factory.setConnection(self)

        # Start looping
        self.loop()

    def setWiiSender(self, wiiSender):
        self.wiiSender = wiiSender

    def iteration(self):
        if None != self.wiiSender:
            self.wiiSender.iteration()
        self.iterationCount += 1

    def sendDataXY(self, deviceIndex, x, y):
        strngData = "%s,%s,%s,%s,%s" % (DT_WII, deviceIndex, MT_XY, x, y)
        if self.factory.verbose:
            print "SENDING:", strngData
        self.sendString(strngData)

    def sendDataButtonDown(self, deviceIndex, x, y, btnId):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_WII, deviceIndex, MT_BUTTONDOWN, x, y, btnId)
        print "Sending Button Down", strngData
        self.sendString(strngData)

    def sendDataButtonUp(self, deviceIndex, x, y, btnId):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_WII, deviceIndex, MT_BUTTONUP, x, y, btnId)
        print "Sending Button Up", strngData
        self.sendString(strngData)

    def loop(self):
        # print "loop"
        try:
            if self.producingInput:
                self.iteration()
        except:
            traceback.print_exc()
        if self.doLoop:
            reactor.callLater(1.0 / self.factory.loopFreq, self.loop)
    
    def stringReceived(self, data):
        if self.factory.verbose:
            print "Data:", data
        # self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print "connection lost"


class WiiSenderClientFactory(protocol.ClientFactory):
    protocol = WiiSenderClientProtocol

    def __init__(self):
        self.verbose = True
        self.loopFreq = 30.0
        self.sendButtonEvents = False
        self.connection = None # there's only one connection
        self.wiiSender = None
        self.devices = {}
        self.largestDeviceIndex=-1

    def getNewDeviceIndex(self, deviceType):
        self.largestDeviceIndex += 1
        return self.largestDeviceIndex

    def registerDevice(self, deviceType, deviceObj):
        #deviceId = getGUID() # FIXME, determine if this should be a simpler id
        deviceIndex = self.getNewDeviceIndex(deviceType)
        deviceId = deviceIndex # works here (not in airstream server) since all ids are created here.
        self.devices[deviceId] = deviceType, deviceIndex, deviceObj
        return deviceId

    def newDataXY(self, deviceId, x, y):
        # note: deviceId == deviceIndex for client
        self.connection.sendDataXY(deviceId, x, y)

    def newDataButtonEvent(self, deviceId, btnId, x, y):
        # note: deviceId == deviceIndex for client
        if btnId == "a": # only send one button for now
            self.connection.sendDataButtonDown(deviceId, x, y, BTN_LEFT)

    def newDataButtonUpEvent(self, deviceId, btnId, x, y):
        # note: deviceId == deviceIndex for client
        if btnId == "a":
            self.connection.sendDataButtonUp(deviceId, x, y, BTN_LEFT)

    def setWiiSender(self, wiiSender):
        self.wiiSender = wiiSender

    def setConnection(self, connection):
        self.connection = connection
        connection.setWiiSender(self.wiiSender)

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        if reactor.running:
            reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        if reactor.running:
            reactor.stop()

    def setVerbose(self, verboseFlag):
        self.verbose = verboseFlag

    def setLoopFreq(self, loopFreq): # msgsPerSec
        self.loopFreq = loopFreq

    def setSendButtonEvents(self, sendButtonEvents):
        self.sendButtonEvents = sendButtonEvents
def parseArgs():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print data")
    parser.add_option("--host",
                      action="store", dest="host", default="localhost",
                      help="airstream server host")
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

    f = WiiSenderClientFactory()
    f.setVerbose(options.verbose)
    f.setLoopFreq(options.loopFreq)

    # create a wii sender
    wiiSender = WiiSender(f, loopFreq=options.loopFreq)
    f.setWiiSender(wiiSender)

    # start a mote detector.  It hands new mote to the wii sender
    moteDetector = MoteDetector(numToConnect=1, detectedCallback=wiiSender.newMote, getAlreadyConnectedIdsCallback=wiiSender.getAlreadyConnectedIds);
    moteDetector.keepFirstConnection=True
    moteDetector.startInThread()

    wiiSender.setMoteDetector(moteDetector)

    print "Connecting to:", options.host, options.port
    reactor.connectTCP(options.host, options.port, f)

    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
