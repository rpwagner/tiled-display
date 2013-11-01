#!/usr/bin/python
from twisted.internet import reactor, protocol
from twisted.protocols.basic import Int16StringReceiver
from asTypes import DT_POINTER,MT_SENDDATA 
import traceback

# A data receiver.
#   Can be used in applications.

class InputClient(Int16StringReceiver):

    def connectionMade(self):
      try:
          print "connection made"
          # Send a msg that we want to receive input data.
          # deviceType, deviceIndex, msgType)
          data = "%s,%s,%s" % (DT_POINTER, -1, MT_SENDDATA)
          self.sendString(data)
          
          self.factory.connectionMade(self)
      except:
          traceback.print_exc()

    #    self.transport.write("hello, world!")
    
    def stringReceived(self, data):
        self.factory.receive(data)
        # self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print "connection lost"

class InputClientFactory(protocol.ClientFactory):
    protocol = InputClient

    def __init__(self):
        self.connectionMadeCallback = None
        self.receiveCallback = None
        self.connectFailedCallback = None
        self.connectionLostCallback = None
        self.verbose = False

    def clientConnectionFailed(self, connector, reason):
        if None == self.connectFailedCallback:
            print "Connection failed - goodbye!"
            if reactor.running:
                reactor.stop()
        else:
            self.connectFailedCallback(reason)
    
    def clientConnectionLost(self, connector, reason):
        if None == self.connectionLostCallback:
            print "Connection lost - goodbye!"
            if reactor.running:
                reactor.stop()
        else:
            self.connectionLostCallback(reason)

    def connectionMade(self, client):
        if None != self.connectionMadeCallback:
            self.connectionMadeCallback(client)

    def receive(self, data):
        if None != self.receiveCallback:
            self.receiveCallback(data)
        else:
            if self.verbose:
                print "Data:", data

    def setConnectionMadeCallback(self, callback):
        self.connectionMadeCallback = callback

    def setReceiveCallback(self, callback):
        self.receiveCallback = callback

    def setConnectFailedCallback(self, callback):
        self.connectFailedCallback = callback

    def setConnectionLostCallback(self, callback):
        self.connectionLostCallback = callback

    def setVerbose(self, verboseFlag):
        self.verbose = verboseFlag

def parseArgs():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print data")
    (options, args) = parser.parse_args()
    return (options, args)

def main():
    (options, args) = parseArgs()

    f = InputClientFactory()
    f.setVerbose(options.verbose)
    reactor.connectTCP("localhost", 11000, f)
    reactor.run()

if __name__ == '__main__':
    main()
