#!/usr/bin/python

from twisted.internet import reactor, protocol
from server import InputServiceProtocol, InputServiceFactory, DT_POINTER
import traceback, random

# A server that also sends random X,Y values
#   Mostly useful for testing.
#   Also, an example of an input device combined
#    with the server.
#   netinput.py or windowSender.py show the more
#     common method of sending data to a remote server.

class InputSimulator:
    def __init__(self, freq, serverObj):
        self.freq = float(freq)
        self.server = serverObj
        self.deviceId = self.server.registerDevice(DT_POINTER, self)
        self.producingInput = False
        print "Sim Not producing input yet"

    def startInputProduction(self):
        print "Sim will now produce input"
        self.producingInput = True

    def stopInputProduction(self):
        self.producingInput = False
        print "Sim will now Not produce input"

    def iteration(self):
        x,y = random.random(), random.random()
        self.server.newDataXY(self.deviceId, x,y) 

    def loop(self):
        # print "loop"
        try:
            if self.producingInput:
                self.iteration()
        except:
            traceback.print_exc()
        reactor.callLater(1.0 / self.freq, self.loop)


def main():
    """This runs the protocol on port 11000"""
    factory = InputServiceFactory()

    factory.protocol = InputServiceProtocol
    reactor.listenTCP(11000,factory)

    input = InputSimulator(100, factory)

    reactor.callLater(0.0, input.loop)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()

