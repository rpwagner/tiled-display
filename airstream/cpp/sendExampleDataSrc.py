import sys, time, math
from twisted.internet import reactor, protocol

sys.path.append("..")

from netinput import InputSenderProtocol, InputClientFactory, parseArgs
import callbackTestDataSrc
from asTypes import BTN_LEFT

libtest = callbackTestDataSrc.setupLib()

# This file mainly reuses classes from netinput.py to send input data to a
#  remote airstream server over the network.
#
#  the callbackTestDataSrc.py module is an example of getting data from c++
#    in case the device mainly has drivers in c or c++

class TestSenderProtocol(InputSenderProtocol):

    def connectionMade(self):
        InputSenderProtocol.connectionMade(self)

        # make cpp update callbacks call our newDataXY(), etc.
        callbackTestDataSrc.registerCallbackObj(self)

    def iteration(self):
        print "test iteration"
        libtest.update()  # might do an update with the defaults until the connection is made
        """
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
        """
        self.iterationCount += 1

    def newDataXY(self, x,y):
        #print "mouseMoved:", x,y
        self.sendDataXY(x,y)

    def buttonDown(self, btnId, x,y):
        #print "buttonDown:", btnId, x,y
        self.sendDataButtonDown(x,y,BTN_LEFT)

    def buttonUp(self, btnId, x,y):
        #print "buttonUp:", btnId, x,y
        self.sendDataButtonUp(x,y,BTN_LEFT)


class TestClientFactory(InputClientFactory):
    protocol = TestSenderProtocol
    def __init__(self):
        InputClientFactory.__init__(self)


def main():
    (options, args) = parseArgs()

    f = TestClientFactory()
    f.setVerbose(options.verbose)
    f.setLoopFreq(options.msgsPerSec)
    f.setSendButtonEvents(options.sendButtonEvents)
    #reactor.connectTCP("localhost", 11000, f)
    print "Connecting to:", options.host, options.port
    reactor.connectTCP(options.host, options.port, f)

    reactor.run()

if __name__ == '__main__':
    main()

