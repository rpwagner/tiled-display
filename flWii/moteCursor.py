import time, sys, os

from mote import detectAllPossible
from moteCache import MoteCache
from mote import Mote
import traceback

from connectToMote import connectToMote
from moteX11 import MoteX11, Rect

class MoteMouseProcessor:
    def __init__(self, connectedMote):
        self.mote = connectedMote

    def processMouse(self):
        # print "processAndUpdateMouse",  self.mote, self.mote.connected, self.mote.irMode
        if self.mote == None or not self.mote.irMode != None:
            return None, None

        # Use standard bar with 2 dots
        #   Must receive at least 2 dots to be valid (and change mouse pos)
        #

        if self.mote.isIrModeFull():
            print "Unimplemented"
        elif self.mote.isIrModeExt():
            print "Unimplemented"
        elif self.mote.isIrModeBasic():
            # the wiimote can report up to 4 points
            #   we'll to convert the two brightest into "base" position so 
            #     we can generate a mouse x,y from them
            pointList = self.mote.extractNormalizedPoints()
            if len(pointList) > 0:
                # print "points:", pointList
                #pointSet = pointList[-1] 
                for pointSet in pointList:
                    # self.updateMinMaxEdge(pointSet)
                    if len(pointSet) > 1:   # just use the frst two points (we're assuming they're the brightest)
                        # We're going to require at least two valid led coordinates (i.e. not 0)
                        if not (pointSet[0][0] == 0.0 or pointSet[1][0] == 0.0 or pointSet[0][1] == 0.0 or pointSet[1][1] == 0.0
                             or pointSet[0][0] == 1.0 or pointSet[1][0] == 1.0 or pointSet[0][1] == 1.0 or pointSet[1][1] == 1.0):
                            midpoint = ( (pointSet[0][0] + pointSet[1][0]) / 2. ,
                                         (pointSet[0][1] + pointSet[1][1]) / 2. )
                            scale = 1.4
                            scaledMidpoint = ( ((midpoint[0]-.5) * scale) + 0.5,
                                               ((midpoint[1]-.5) * scale) + 0.5)
                            # print "Setting mouse pos:", scaledMidpoint
                            #self.moteX11.setMousePosNormalized(1.0 - scaledMidpoint[0], scaledMidpoint[1])
                            return (1.0-scaledMidpoint[0], scaledMidpoint[1])
            """
            pt = self.mote.extractLastNormalizedPoint()
            if pt != None:
                scale = 1.4
                scaledPoint = ( ((pt[0]-.5) * scale) + 0.5,
                                       ((pt[1]-.5) * scale) + 0.5)
                self.moteX11.setMousePosNormalized(1.0 - scaledPoint[0], scaledPoint[1])
            """

        else: # basic
            print "Unhandled ir mode:", self.mote.irMode
            print "DEBUG:", self.mote, self.mote.connected
            raise Exception("Unhandled ir mode")

        return None, None


class MoteMouse(MoteMouseProcessor):
    def __init__(self, connectedMote, moteX11):
        MoteMouseProcessor.__init__(self, connectedMote)
        # self.mote = connectedMote  # done in parent class
        self.moteX11 = moteX11

    def processAndUpdateMouse(self):
        x, y = MoteMouseProcessor.processMouse(self)
        if x != None:
            self.moteX11.setMousePosNormalized(x, y)


if __name__ == "__main__":

    mote = connectToMote()

    x = MoteX11() 

    try:
        x.connectToX()

        moteMouse = MoteMouse(mote,x)

        while 1:
            moteMouse.processAndUpdateMouse()
            time.sleep(0.0001)
    except:
        traceback.print_exc()
    finally:
        mote.disconnect()
        if mote.readThread != None:
            print "Exiting, joining thread"
            mote.readThread.join()

