#!/usr/bin/python

# Opens an window and sends mouse and keyboard input from
#   it to an airstream server.
#   This file and netinput.py are also good starting
#   points for writing a sender for a new device.

import os, sys, time, traceback

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.pmath.vec2 import *
from flapp.RuleSystem.triggers import *
from flapp.app import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from flapp.RuleSystem import ruleSystem
from flapp.glDrawUtils import Draw2dSquareIn2D, ScreenClearer

from netinput import InputSenderProtocol, InputClientFactory
from twisted.internet import reactor, protocol

from asTypes import DT_POINTER, MT_DONTSENDDATA, MT_XY, MT_BUTTONDOWN, MT_BUTTONUP, BTN_LEFT


class UserGeneratedInputSenderProtocol(InputSenderProtocol):

    def connectionMade(self):
        try:
            print "connection made UserGeneratedInputSenderProtocol"
            # Send a msg that we don't want to receive input data.
            # deviceType, deviceIndex, msgType)
            data = "%s,%s,%s" % (DT_POINTER, -1, MT_DONTSENDDATA)
            self.sendString(data)
        except:
            traceback.print_exc()

        self.doLoop=False ### don't loop
        #self.loopFreq = 30.0  # leave setting in factory for now
        self.producingInput = True
        reactor.callLater(0.0, self.loop)
        self.startTime = 0.0
        self.iterationCount = 0
        self.factory.connectionMade(self)

    def iteration(self):
        print "iteration"  # don't want to loop over this.

class UserGeneratedInputClientFactory(InputClientFactory):
    protocol = UserGeneratedInputSenderProtocol

    def __init__(self):
        self.verbose = True
        self.loopFreq = 30.0
        self.sendButtonEvents = False
        self.connection = None
        self.app = None
        self.connectionMadeCallback=None

    def connectionMade(self, connection):
        self.setConnection(connection)
        if self.connectionMadeCallback:
            self.connectionMadeCallback(self)

    def setConnectionMadeCallback(self, callback):
        self.connectionMadeCallback=callback

    def setConnection(self, connection):
        self.connection = connection

    def setApp(self, app):
        self.app = app

    def clientConnectionLost(self, connector, reason):
        print "Connection lost (UserGeneratedInputClientFactory).  Quitting."
        if reactor.running:
            reactor.callLater(1.0, reactor.stop)
            #reactor.stop()
        if self.app:
            self.app._running = 0

class MouseEventHandler:
    def __init__(self, client, app):
        self.client = client
        self.lastMotionSentTime = time.time()
        self.lastMouseLocation = 0,0
        self.app=app

    def normalizeMouseCoords(self, x,y):
        return float(x)/self.app.width, float(y)/self.app.height

    def mouseEvent(self, trigger, event):  # event: [eventtype, eventbutton, (posx,posy), event ]
        print "mouseEvent"
        eventType = event[0]
        buttonid = event[1]
        buttonid = self.convertSDLMouseButtonToVL3(buttonid)
        xcoord, ycoord = event[2]

        normxcoord, normycoord = self.normalizeMouseCoords(xcoord, ycoord)
        if eventType == MOUSEBUTTONDOWN:
            #self.client.sendEvent("MouseDown", [xcoord,ycoord, buttonid])
            if self.client.connection:
                self.client.connection.sendDataButtonDown(normxcoord,normycoord, buttonid)
        elif eventType == MOUSEBUTTONUP:
            #self.client.sendEvent("MouseUp", [xcoord,ycoord, buttonid])
            if self.client.connection:
                self.client.connection.sendDataButtonUp(normxcoord,normycoord, buttonid)
        else:
            print "WARNING: Unhandled mouse event of type: ", eventType

        self.lastMouseLocation = xcoord, ycoord

        # self.client.sendEvent("Snapshot", "blah")

    def convertSDLMouseButtonToVL3(self, buttonid):
        return buttonid-1

    def mouseMotionEvent(self, trigger, event):  # event: [eventtype, eventbutton, (posx,posy), event ]
        xcoord, ycoord = event[0]
        if time.time() - self.lastMotionSentTime > 0.05: # no more than 20 per second
            self.lastMotionSentTime = time.time()
            #self.client.sendEvent("MouseMove", [xcoord,ycoord])
            normxcoord, normycoord = self.normalizeMouseCoords(xcoord, ycoord)
            if self.client.connection:
                self.client.connection.sendDataXY(normxcoord,normycoord)
        #else:
        #    print "skipped one"

        self.lastMouseLocation = xcoord, ycoord

    def keyRelease(self, trigger, event):  # event: [eventtype, eventbutton, (posx,posy), event ]
        print event, type(event[0])
        keyid = event[0]
        normxcoord, normycoord = self.normalizeMouseCoords(*self.lastMouseLocation)
        self.client.connection.sendDataKeyUp(keyid, normxcoord, normycoord)

    def keyPress(self, trigger, event):  # event: [eventtype, eventbutton, (posx,posy), event ]
        try:
            print event, type(event[0])
            keyid = event[0]
            keyAsStr = chr(keyid)
            normxcoord, normycoord = self.normalizeMouseCoords(*self.lastMouseLocation)
            self.client.connection.sendDataKeyDown(keyAsStr, normxcoord, normycoord)

            # Example of sending a dataString such as "quit"
            #if keyAsStr == "q": # help to verify sendString also works
            #    self.client.connection.sendDataString("quit")

            """ # string example:
            if chr(keyid) == 'p':
                if self.client.connection:
                    self.client.connection.sendDataString("togglepause")
            """
        except Exception, e:
            traceback.print_exc()

    def getPos(self):
        return self.lastMouseLocation


class Pointer:
    # simple class to draw the pointer position
    def __init__(self, positionSource):
        self.pos = Vec2(50,50)
        self.cursorSize = Vec2(10,10)
        self.positionSource = positionSource

    def draw(self, renderer):
        Draw2dSquareIn2D( self.pos, self.cursorSize[0], self.cursorSize[1])

    def update(self, secs, app):
        #print self.positionSource.getPos()
        self.pos.set(self.positionSource.getPos()[0]-self.cursorSize[0]/2,
                     app.height-self.positionSource.getPos()[1]-self.cursorSize[1]/2)




def run(host=None, port=None, width=1024, height=768, doReturn=False):

    # Setup connection
    print "Setting up connection"
    f = UserGeneratedInputClientFactory()
    f.setVerbose(True)
    #f.setVerbose(options.verbose)
    #f.setLoopFreq(options.msgsPerSec)
    #f.setSendButtonEvents(options.sendButtonEvents)
    print "Connecting to:", host, port
    reactor.connectTCP(host, port, f)

    # --------
    print "setting up UI"
    windowWidth = width #1000# 320
    windowHeight = height # 800 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    renderer.addFrameSetupObj(ScreenClearer())
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight)


    mouseHandler = MouseEventHandler(f, app=app)

    app.addDynamicObject(Pointer(mouseHandler))

    app.addTriggerResponse(TriggerOnMouseEvent(), ruleSystem.Response("HandleMouseEvent", mouseHandler.mouseEvent, []) )
    app.addTriggerResponse(TriggerOnMouseMotionEvent(), ruleSystem.Response("HandleMouseMotionEvent", mouseHandler.mouseMotionEvent, []) )
    app.addTriggerResponse(TriggerWhenAnyKeyPressed(), ruleSystem.Response("HandleKeyPress", mouseHandler.keyPress, []) )
    app.addTriggerResponse(TriggerWhenAnyKeyReleased(), ruleSystem.Response("HandleKeyRelease", mouseHandler.keyRelease, []) )


    #box = glBox()
    #app.addDynamicObject(box)
    #glEnable(GL_TEXTURE_2D)

    if doReturn:
        return app
    else:
        app.runWithTwisted()
        print "Exiting."

if __name__ == "__main__":
  if (len(sys.argv) > 4):
      host = sys.argv[1]
      port = int(sys.argv[2])
      width = int(sys.argv[3])
      height = int(sys.argv[4])
      run(host, port, width, height)
  elif (len(sys.argv) > 2):
      host = sys.argv[1]
      port = int(sys.argv[2])
      run(host, port)
  else:
      print "Usage: ", sys.argv[0], "<airstreamhost> <airstreamport> <width> <height>"

