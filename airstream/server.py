#!/usr/bin/python
from twisted.internet import reactor, protocol
from twisted.protocols.basic import Int16StringReceiver
from twisted.internet.protocol import Protocol, ServerFactory
import time

from GUID import getGUID
from asTypes import *


class InputServiceProtocol(Int16StringReceiver):

    def __init__(self):
        pass

    def connectionMade(self):
        # self.transport.write("hello, world!")
        print "connectionMade (protocol)", self
        self.factory.connectionMade(self)

    def connectionLost(self, reason):
        print "connection lost (protocol)", self
        self.factory.removeConnection(self)
    
    def stringReceived(self, data):
        self.factory.bytesReceived += len(data)
        self.factory.numMsgsReceived += 1

        # self.transport.write(data)
        if self.factory.verbose:
            print "STRING RECEIVED:", data
        words = data.split(",")

        deviceType, deviceIndex, msgType = words[:3]
        deviceType, deviceIndex, msgType = int(deviceType), int(deviceIndex), int(msgType)
        if msgType == MT_DONTSENDDATA:
            print "received msg dont send data.", msgType
            self.factory.setSendData(False, self)
        elif msgType == MT_SENDDATA:
            print "received msg send data.", msgType
            self.factory.setSendData(True, self)
        elif msgType == MT_XY:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            x,y = words[3:5]
            self.factory.newDataXY(deviceIndex, float(x), float(y))
        elif msgType == MT_BUTTONDOWN:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            x,y,btnId = words[3:6]
            self.factory.newDataButtonDown(deviceIndex, float(x), float(y), btnId)
        elif msgType == MT_BUTTONUP:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            x,y,btnId = words[3:6]
            self.factory.newDataButtonUp(deviceIndex, float(x), float(y), btnId)
        elif msgType == MT_STRING:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            stringArg = words[3]
            self.factory.newDataString(deviceIndex, stringArg)
        elif msgType == MT_KEYDOWN:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            key,x,y = words[3:6]
            self.factory.newDataKeyDown(deviceIndex, key, float(x), float(y))
        elif msgType == MT_KEYUP:
            # get a device index.  Register as a sender if this connection is new.
            deviceIndex = self.factory.getOrCreateDeviceIndexForConnection(self, deviceType=deviceType)
            key,x,y = words[3:6]
            self.factory.newDataKeyUp(deviceIndex, key, float(x), float(y))
        else:
            print "WARNING: Unhandled MsgType received on server: ", msgType
         
        # (deviceType, deviceIndex, msgType, n, n, n, n)


class InputServiceFactory(ServerFactory):

    def __init__(self):
        self.inputDevices = {}
        self.largestDeviceIndex = -1
        self.connections = []
        self.connectionsReceivingInput = []
        self.connectionsSendingOverNetwork = {} # connection: deviceIndex
        self.inputsBeingConsumed = False

        # for output printing:
        self.verbose = True
        self.performanceDisplayDelay = 2
        self.lastDisplay = time.time()
        self.numMsgsReceived = 0
        self.numMsgsSent = 0
        self.bytesSent = 0
        self.bytesReceived = 0

    def connectionMade(self, connection):
        print "connection made (factory)"
        self.connections.append(connection)
        # client should send a MT_SENDDATA msg to start receiving.
        #self.connectionsReceivingInput.append(connection)
        #self.verifyInputProduction()

    def removeConnection(self, connection):
        print "connection lost (factory)"
        self.connections.remove(connection)
        if connection in self.connectionsReceivingInput:
            self.connectionsReceivingInput.remove(connection)
        self.verifyInputProduction()

    def verifyInputProduction(self):
        previouslyBeingConsumed = self.inputsBeingConsumed
        if len(self.connectionsReceivingInput) > 0 and False == previouslyBeingConsumed:
            self.startInputProduction()
        elif len(self.connectionsReceivingInput) == 0 and True == previouslyBeingConsumed:
            self.stopInputProduction()
        print "VERIFY:", len(self.inputDevices), previouslyBeingConsumed, self.inputsBeingConsumed

    def startInputProduction(self):
        print "factory: start input production"
        for deviceType, deviceIndex, deviceObj in self.inputDevices.values():
            if deviceObj:
                deviceObj.startInputProduction()
        self.inputsBeingConsumed = True

    def stopInputProduction(self):
        print "factory: stop input production"
        for deviceType, deviceIndex, deviceObj in self.inputDevices.values():
            if deviceObj:
                deviceObj.stopInputProduction()
        self.inputsBeingConsumed = False
            

    def getNewDeviceIndex(self, deviceType):
        self.largestDeviceIndex += 1
        return self.largestDeviceIndex
        #nextIndex = 0
        #for dType, dIndex in self.devices.values(): 
        #    if dType == deviceType:
        #        nextIndex = max(dIndex+1, nextIndex)
        #return nextIndex

    def newDataXY(self, deviceId, x, y):
        # data type, device name/number, message type
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s,%s" % (deviceType, deviceIndex, MT_XY, x, y)
        self.sendNewData(strng)

    def newDataButtonDown(self, deviceId, x, y, btnId):
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s,%s,%s" % (deviceType, deviceIndex, MT_BUTTONEVENT, x, y, btnId)
        self.sendNewData(strng)

    def newDataButtonUp(self, deviceId, x, y, btnId):
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s,%s,%s" % (deviceType, deviceIndex, MT_BUTTONUPEVENT, x, y, btnId)
        self.sendNewData(strng)

    def newDataString(self, deviceId, stringArg):
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s" % (deviceType, deviceIndex, MT_STRING, stringArg)
        self.sendNewData(strng)

    def newDataKeyDown(self, deviceId, key, x, y):
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s,%s,%s" % (deviceType, deviceIndex, MT_KEYDOWN, key, x, y)
        self.sendNewData(strng)

    def newDataKeyUp(self, deviceId, key, x, y):
        deviceType, deviceIndex, deviceObj = self.inputDevices[deviceId]
        strng = "%s,%s,%s,%s,%s,%s" % (deviceType, deviceIndex, MT_KEYUP, key, x, y)
        self.sendNewData(strng)

    def sendNewData(self, dataStrng):
        #for connection in self.connections:
        for connection in self.connectionsReceivingInput:
            # connection.transport.write(dataStrng)
            self.numMsgsSent += 1
            self.bytesSent += len(dataStrng)
            connection.sendString(dataStrng)

    def registerDevice(self, deviceType, deviceObj):
        deviceId = getGUID() # FIXME, determine if this should be a simpler id
        deviceIndex = self.getNewDeviceIndex(deviceType)
        self.inputDevices[deviceId] = deviceType, deviceIndex, deviceObj
        return deviceId

    def getOrCreateDeviceIndexForConnection(self, connection, deviceType=None):
        if connection not in self.connectionsSendingOverNetwork:
            deviceId = self.registerDevice(deviceType, None)
            self.connectionsSendingOverNetwork[connection] = deviceId

        return self.connectionsSendingOverNetwork[connection]

    def unregisterDevice(self, deviceId):
        del self.inputDevices[deviceId]

    def setSendData(self, sendDataFlag, connection):
        if False == sendDataFlag:
            if connection in self.connectionsReceivingInput:
                self.connectionsReceivingInput.remove(connection)
        elif True == sendDataFlag:
            if connection not in self.connectionsReceivingInput:
                self.connectionsReceivingInput.append(connection)
        else: # True
            raise Exception("Invalid data flag: " + str(sendDataFlag))

        self.verifyInputProduction()

    def setVerbose(self, verboseFlag=False):
        self.verbose = verboseFlag

    def displayPerformance(self):
        delta = time.time() - self.lastDisplay
        if delta > 0:
            print "Received Msgs/sec: %.2f, Bytes/sec: %.2f" % ( self.numMsgsReceived / delta, self.bytesReceived / delta )
            print "Sent Msgs/sec: %.2f Bytes/sec: %.2f" % ( self.numMsgsSent / delta, self.bytesSent / delta )
        # reset for next iteration
        self.numMsgsReceived = 0
        self.numMsgsSent = 0
        self.bytesReceived = 0
        self.bytesSent = 0
        reactor.callLater(self.performanceDisplayDelay, self.displayPerformance)
        self.lastDisplay = time.time()


def parseArgs(argv=None):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print data")
    parser.add_option("--port",
                      dest="port", default=11000,
                      type="int", help="server port")
    parser.add_option("--perf",
                      action="store_true", dest="perf", default=False,
                      help="print perf data")
    (options, args) = parser.parse_args(args=argv)
    return (options, args)


def main( argv=None ):

    (options, args) = parseArgs(argv)

    if options.perf:
        options.verbose = False

    #factory = protocol.ServerFactory()
    factory = InputServiceFactory()
    factory.protocol = InputServiceProtocol
    factory.setVerbose(options.verbose)
    reactor.listenTCP(options.port,factory)
    if options.perf:
        reactor.callLater(factory.performanceDisplayDelay, factory.displayPerformance)
    reactor.run()

if __name__ == '__main__':
    main()

