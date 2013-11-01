#!/usr/bin/python

# An input receiver that receives mouse events
#  from the airstream server and sends them to
#  the local X server.
#  Simple keyboard support works, but shift and
#  other modifier keys haven't been implemented yet.
 

from flWii.moteKeysAndMouse import MoteX11WithKeysAndMouse
from client import InputClient, InputClientFactory
from asTypes import MT_BUTTONEVENT, MT_BUTTONUPEVENT, MT_XY, MT_KEYDOWN, MT_KEYUP
from twisted.internet import reactor

class InputClientX11(InputClient):
    def __init__(self):

        self.x = MoteX11WithKeysAndMouse()
        # self.x.printInfo = False
        self.x.connectToX()
        #moteMouse = MoteMouse(mote,x)
        #moteKeys = MoteKeys(mote, x, buttonMappings)

    def stringReceived(self, data):
        print "Data:", data
        words = data.split(",")
        deviceType, deviceIndex, msgType = words[:3]
        if int(msgType) == MT_XY: 
            x,y = words[3:5]
            self.x.setMousePosNormalized(float(x),float(y))
        elif int(msgType) == MT_BUTTONEVENT: 
            print "RECEIVED BUTTONEVENT"
            x,y = words[3:5]
            btnId = int(words[5])
            self.x.setMousePosNormalized(float(x),float(y))
            self.x.sendMouseButton(btnId, isDown=True)
        elif int(msgType) == MT_BUTTONUPEVENT: 
            print "RECEIVED BUTTONUPEVENT"
            x,y = words[3:5]
            btnId = int(words[5])
            print "X,Y:", x, y, float(x), float(y)
            self.x.setMousePosNormalized(float(x),float(y))
            self.x.sendMouseButton(btnId, isDown=False)
        elif int(msgType) == MT_KEYDOWN: 
            print "RECEIVED KEYDOWN", data
            key = int(words[3])
            x,y = words[4:6]
            print "X,Y:", x, y, float(x), float(y)
            self.x.setMousePosNormalized(float(x),float(y))
            try:
                self.x.sendKeyPress(chr(key))
                print "Sending key down to x:", key, chr(key)
            except Exception, e:
                print e
        elif int(msgType) == MT_KEYUP: 
            print "RECEIVED KEYUP", data
            key = int(words[3])
            x,y = words[4:6]
            self.x.setMousePosNormalized(float(x),float(y))
            try:
                self.x.sendKeyRelease(chr(key))
                print "Sending key up to x:", key, chr(key)
            except Exception, e:
                print "Error sending key:", e
        else:
            print "ERROR, invalid msgType:", msgType
        
        # self.transport.loseConnection()

def main():
    f = InputClientFactory()
    f.protocol = InputClientX11
    reactor.connectTCP("localhost", 11000, f)
    reactor.run()

if __name__ == '__main__':
    main()
