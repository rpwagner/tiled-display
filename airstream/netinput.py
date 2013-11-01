#!/usr/bin/python

# Sends generated input to an airstream server.
#   Useful as a quick test of the server.
#   This file and windowSender.py are also good starting
#   points for writing a sender for a new device.

import math, traceback, time
from twisted.internet import reactor, protocol
from twisted.protocols.basic import Int16StringReceiver
from asTypes import DT_POINTER, MT_DONTSENDDATA, MT_XY, MT_BUTTONDOWN, MT_BUTTONUP, MT_STRING, BTN_LEFT, MT_KEYDOWN, MT_KEYUP

class InputSenderProtocol(Int16StringReceiver):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        try:
            print "connection made InputSenderProtocol"
            # Send a msg that we don't want to receive input data.
            # deviceType, deviceIndex, msgType)
            data = "%s,%s,%s" % (DT_POINTER, -1, MT_DONTSENDDATA)
            self.sendString(data)
        except:
            traceback.print_exc()
     
        self.doLoop=True
        #self.loopFreq = 30.0  # leave setting in factory for now
        self.producingInput = True
        reactor.callLater(0.0, self.loop)
        self.startTime = 0.0
        self.iterationCount = 0


    def iteration(self):
        print "iteration"
        t = time.time() - self.startTime
        x = math.sin(t)
        y = math.cos(t)
        if self.factory.sendButtonEvents:
            if self.iterationCount % 100 == 30:  # press on 30
                self.sendDataButtonDown(x,y, BTN_LEFT)
            elif self.iterationCount % 100 == 70: # release on 70
                self.sendDataButtonUp(x,y, BTN_LEFT)
            else:
                self.sendDataXY(x,y)
        else:
            self.sendDataXY(x,y)
        self.iterationCount += 1

    def sendDataXY(self, x, y):
        strngData = "%s,%s,%s,%s,%s" % (DT_POINTER, -1, MT_XY, x, y)
        self.sendString(strngData)

    def sendDataString(self, stringArg):
        strngData = "%s,%s,%s,%s" % (DT_POINTER, -1, MT_STRING, stringArg)
        self.sendString(strngData)

    def sendDataButtonDown(self, x, y, btnId):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_POINTER, -1, MT_BUTTONDOWN, x, y, btnId)
        print "Sending Button Down"
        self.sendString(strngData)

    def sendDataButtonUp(self, x, y, btnId):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_POINTER, -1, MT_BUTTONUP, x, y, btnId)
        print "Sending Button Up"
        self.sendString(strngData)

    def sendDataKeyDown(self, key, x, y):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_POINTER, -1, MT_KEYDOWN, key, x, y)
        print "Sending Key Down", key, x, y
        self.sendString(strngData)

    def sendDataKeyUp(self, key, x, y):
        strngData = "%s,%s,%s,%s,%s,%s" % (DT_POINTER, -1, MT_KEYUP, key, x, y)
        print "Sending Key Up", key, x, y
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

class InputClientFactory(protocol.ClientFactory):
    protocol = InputSenderProtocol

    def __init__(self):
        self.verbose = True
        self.loopFreq = 30.0
        self.sendButtonEvents = False

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
    parser.add_option("-b", "--buttonEvents",
                      action="store_true", dest="sendButtonEvents", default=False,
                      help="send button events")
    parser.add_option("-m", "--msgsPerSec",
                      action="store", type="float", dest="msgsPerSec",
                      default=30.0, help="set msgs per second to send")
    (options, args) = parser.parse_args()
    return (options, args)


def main():
    (options, args) = parseArgs()

    f = InputClientFactory()
    f.setVerbose(options.verbose)
    f.setLoopFreq(options.msgsPerSec)
    f.setSendButtonEvents(options.sendButtonEvents)
    #reactor.connectTCP("localhost", 11000, f)
    print "Connecting to:", options.host, options.port
    reactor.connectTCP(options.host, options.port, f)

    reactor.run()

if __name__ == '__main__':
    main()

