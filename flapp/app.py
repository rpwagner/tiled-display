import os, sys
import traceback
import pygame
import time
from pygame.locals import *

from flapp.callLaterList import CallLaterList

try:
    import pygame.fastevent as eventmodule
    print "using fastevent"
    UsingFastEvent = True
except ImportError:
    print "not using fastevent"
    UsingFastEvent = False
    import pygame.event as eventmodule


# --- (begin) enable pygame use with twisted ---
global HaveTwisted 
HaveTwisted = False

try:
    from twisted.internet import threadedselectreactor
    HaveTwisted = True
except:
    try:
        from twisted.internet import _threadedselect as threadedselectreactor
        HaveTwisted = True
    except:
        HaveTwisted = False

try:
    threadedselectreactor.install()
except:
    pass

from pygame import event
if HaveTwisted: # if 'twisted' in globals():
    from twisted.internet import reactor
    TWISTEDEVENT = USEREVENT

def postTwistedEvent(func):
    # if not using pygame.fastevent, this can explode if the queue
    # fills up.. so that's bad.  Use pygame.fastevent, in pygame CVS
    # as of 2005-04-18.
    eventmodule.post(eventmodule.Event(TWISTEDEVENT, iterateTwisted=func))

# ----- newer example:
NUM_EVENTS_TO_POST = 200000

from threading import Thread

class post_them(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.done = []
        self.stop = []

    def run(self):
        self.done = []
        self.stop = []
        for x in range(NUM_EVENTS_TO_POST):
            ee = event.Event(USEREVENT)
            try_post = 1

            # the pygame.event.post raises an exception if the event
            #   queue is full.  so wait a little bit, and try again.
            while try_post:
                try:
                    eventmodule.post(ee)
                    try_post = 0
                except:
                    pytime.sleep(0.001)
                    try_post = 1
                
            if self.stop:
                return
        self.done.append(1)

# --- (end) enable pygame use with twisted ---

from RuleSystem import ruleSystem
from RuleSystem.ruleSystem import Rule

class BaseObject:
    def __init__(self):
        self.children = []

    def updateChildren(self, app, secs):
        for child in self.children:
            child.update(app, secs)

    def update(self, app, secs):
        self.updateChildren()

    def addChild(self, child):
        self.children.append(child)

    def removeChild(self, child):
        self.children.remove(child)

class App:
    def __init__(self, width, height):
        self.verbose = 0
        self._running = 0
        self._paused = False
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.printFPS = False
        self._tickClock()
        self.renderers = []
        self.resizable = False
        self.ruleSystem = ruleSystem.RuleSystem()
        self.pauseKeys = [K_p]
        self.mouseGrabbed = False

        # Object lists
        self.dynamicObjects = []
        self.staticObjects = []
        self.windowObjects = []  # 2D window objects such as border, buttons, text
        self.dynamicObjectsToBeRemoved = []
        self.staticObjectsToBeRemoved = []
        self.windowObjectsToBeRemoved = []

        self.callLaterList = CallLaterList()


    def initialize(self, fullscreen=False, windowBorder=True):
        self.fullscreen=fullscreen
        self.hasBorder = windowBorder
        if "SDL_VIDEO_WINDOW_POS" in os.environ:
            print "Before pygame.init: SDL_VIDEO_WINDOW_POS:", os.environ["SDL_VIDEO_WINDOW_POS"]
        pygame.init()
        self._initDisplay()

        self._tickClock()
        self._running = 0
        self._paused = 0

    def _initDisplay(self):
        self.videoFlags =  pygame.DOUBLEBUF | pygame.OPENGL
        if self.fullscreen:
            self.videoFlags |= pygame.FULLSCREEN
        if not self.hasBorder:
            self.videoFlags |= pygame.NOFRAME
        if self.resizable:
            self.videoFlags |= pygame.RESIZABLE

        print "SET VIDEO MODE:", (self.width,self.height)
        self.screen = pygame.display.set_mode((self.width,self.height), self.videoFlags)

    def mainLoopIteration(self, handleEvents=True):
        self._tickClock()
        if handleEvents:
            self.handleEvents()
        else: # a couple calls that are in handleEvents() still needed
            self.callLaterList.checkCallAndRemove()
            self.postHandleEvents()

        self.removeObjectsWaitingToBeRemoved()

        if not self._paused:
            self.updateObjects() # move
        for renderer in self.renderers:
            renderer.draw()
        pygame.display.flip() # Performs gl swap buffer

        self.updateMouse()

    def run(self):
        self._tickClock() # don't include time during initialization
        self._running = 1
        while self._running:
            self.mainLoopIteration()

    def setRenderer(self, renderer):
        #self.renderer = renderer
        self.renderers = [renderer]

    def addRenderer(self, renderer):
        self.renderers.append(renderer)

    def updateObjects(self):
        for obj in self.dynamicObjects:
            obj.update(self.deltaSecs, self)
            
    def _tickClock(self):
        deltaMilliSecs = self.clock.tick(130)
        if deltaMilliSecs == 0:
            deltaMilliSecs = 1
        self.deltaSecs = deltaMilliSecs * .001
        #print "TICK:", self.deltaSecs
        if True == self.printFPS:
            print "FPS:", 1 / ( self.deltaSecs ), "py fps:", self.clock.get_fps()

    def handleEvents(self):
        # Handle events
        for event in pygame.event.get():
            self.handleOneEvent(event)

        self.callLaterList.checkCallAndRemove()

        self.postHandleEvents()

    def postHandleEvents(self):
        pass

    def callLater(self, secs, func, args):
        self.callLaterList.add(secs, func, args)

    def handleOneEvent(self, event):
        try:
            if event.type in ([QUIT]):
                self._running = 0
            elif event.type in ([VIDEORESIZE]):
                print "RESIZE:", event, dir(event)
                for renderer in self.renderers:
                    renderer.reshape(event.w,event.w)
                self.triggerRule("Resize", [event.w, event.h] )
            elif event.type in (MOUSEMOTION,):
                self.triggerRule("MouseMotion", [event.pos, event.rel, event.buttons] )
            elif event.type in (KEYDOWN, KEYUP):
                if K_ESCAPE == event.key:
                    self._running = 0
                #elif K_p == event.key:
                elif event.key in self.pauseKeys:
                    if event.type == KEYDOWN:
                        self._paused = not self._paused

                if event.type == KEYDOWN:
                    self.triggerRule("KeyPress_" + str(event.key))
                    # trigger generic rule
                    self.triggerRule("KeyPress", [event.key, event])
                elif event.type == KEYUP:
                    self.triggerRule("KeyRelease_" + str(event.key))
                    self.triggerRule("KeyRelease", [event.key, event])

                # Send the event for things waiting for both up and down.
                self.triggerRule("KeyEvent", [event.key, event.type, event.mod, event])

            elif event.type in ([JOYBUTTONDOWN, JOYBUTTONUP]):
                button = self.joystickLookup(event.joy, event.button)
                self.triggerRule("JoyButton", [event.joy, button, event.type, event])

            elif event.type in ([MOUSEBUTTONDOWN, MOUSEBUTTONUP]):
                self.triggerRule("MouseEvent", [event.type, event.button, event.pos, event])
        except:
            traceback.print_exc()


    def addStaticObject(self, obj):
        if (None != obj):
            self.staticObjects.append(obj)
            for renderer in self.renderers:
                renderer.addStaticObject(obj)

    def removeStaticObject(self, obj):
        self.staticObjectsToBeRemoved.append(obj)

    def _removeStaticObject(self, obj):
        if (obj in self.staticObjects):
            self.staticObjects.remove(obj)
            for renderer in self.renderers:
                renderer.removeStaticObject(obj)

    def addDynamicObject(self, obj, addToRenderer=True):
        if (None != obj):
            self.dynamicObjects.append(obj)
            if addToRenderer:
                for renderer in self.renderers:
                    renderer.addDynamicObject(obj)

    def removeDynamicObject(self, obj):
        self.dynamicObjectsToBeRemoved.append(obj)

    def _removeDynamicObject(self, obj):
        if (obj in self.dynamicObjects):
            self.dynamicObjects.remove(obj)
            for renderer in self.renderers:
                renderer.removeDynamicObject(obj)

    def removeObjectsWaitingToBeRemoved(self):
        for obj in self.dynamicObjectsToBeRemoved:
            self._removeDynamicObject(obj)
        self.dynamicObjectsToBeRemoved = []
        for obj in self.staticObjectsToBeRemoved:
            self._removeStaticObject(obj)
        self.staticObjectsToBeRemoved = []
        for obj in self.windowObjectsToBeRemoved:
            self._removeWindowObject(obj)
        self.windowObjectsToBeRemoved = []

    def addWindowObject(self, obj):
        if None != obj:
            self.windowObjects.append(obj)
            for renderer in self.renderers:
                renderer.addScreenObject(obj)

    def removeWindowObject(self, obj):
        self.windowObjectsToBeRemoved.append(obj)

    def _removeWindowObject(self, obj):
        if obj in self.windowObjects:
            self.windowObjects.remove(obj)
            for renderer in self.renderers:
                renderer.removeScreenObject(obj)

    def setTitle(self, name):
        pygame.display.set_caption(name)

    def triggerRule(self, trigger_name, args=[]):
        # print "Trigger rule", trigger_name
        self.ruleSystem.triggerRule(trigger_name, args)

    def addTriggerResponse(self, trigger, response):
        self.ruleSystem.addRule( Rule(trigger, response) )

    def removeTriggerResponse(self, trigger, response):
        self.ruleSystem.removeRule( Rule(trigger,response) )

    # Testing for use with twisted
    def eventIterator(self):
        while True:
            # print "***"
            # ---
            # self._tickClock() # 20100908 got rid of this, move to looping call
            #20070820 if not self._paused:
            #20070820    self.updateObjects() # move
            # ---
            if UsingFastEvent:
                #print "Yielding"
                yield eventmodule.wait() # seems to hang otherwise
                #print "Done Yielding"
            while True:
                event = eventmodule.poll()
                if event.type == NOEVENT:
                    break
                else:
                    yield event
            # ---
            # print "***---"
            """ # 20100908 trying looping call instead of doing it here
                #  it's not really getting here anyway.
            try:
                self.mainLoopIteration()
            except:
                traceback.print_exc()
            """
            #20070820 self.postHandleEvents()
            #20070820 self.renderer.draw()
            #20070820 pygame.display.flip()
            # ---

    def runWithTwisted(self, verbose=False):
        if hasattr(eventmodule, 'init'):
            eventmodule.init()

        # send an event when twisted wants attention
        reactor.interleave(postTwistedEvent)

        # make shouldQuit a True value when it's safe to quit 
        # by appending a value to it.  This ensures that
        # Twisted gets to shut down properly.
        shouldQuit=[]
        reactor.addSystemEventTrigger('after', 'shutdown', shouldQuit.append, True)

        # Have our main "app" iteration called repeatedly
        #    pygame events are handled in the loop below, so also don't have
        #    the mainLoop iteration handle pygame events.
        reactor.callLater(.0, self.twistedOutside_mainLoopIterationDontHandleEvents)

        self._running = 1
        while self._running:
            #self._tickClock()
            #if not self._paused:
            #    self.updateObjects() # move
            # **** organize this so it integrates with non-twisted events.
            for event in self.eventIterator():  # this is an infinite loop
                if event.type == TWISTEDEVENT:
                    event.iterateTwisted()
                    if shouldQuit:
                        self._running = 0
                        break
                #elif event.type == QUIT:
                #    reactor.stop()
                else:  # *** should we instead pass all events and move this
                       #    handling into current event handling?
                    self.handleOneEvent(event)
            #self.renderer.draw()
            #pygame.display.flip()
        if verbose:
            print "mainloop in app.runWithTwisted done"
            pygame.quit()
            print "pygame.quit done"
        print "app.runWithTwisted done"

    def runWithTwisted2(self):
        if hasattr(eventmodule, 'init'):  # for fastevents
            eventmodule.init()

        poster = post_them()

        poster.start()

        while 1:
            #for e in event.get():
            #for x in range(200):
            #    ee = event.Event(USEREVENT)
            #    r = event_module.post(ee)
            #    print r
            
            #for e in event_module.get():
            event_list = []
            event_list = eventmodule.get()

            for e in event_list:
                if e.type == QUIT:
                    print c.get_fps()
                    poster.stop.append(1)
                    return
                elif e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        print c.get_fps()
                        poster.stop.append(1)
                else:  # *** should we instead pass all events and move this
                       #    handling into current event handling?
                    self.handleOneEvent(e)
                    return

            """
            if poster.done:
                print c.get_fps()
                print c
                t2 = pytime.time()
                print "total time:%s" % (t2 - t1)
                print "events/second:%s" % (NUM_EVENTS_TO_POST / (t2 - t1))
                return
            #if with_display:
            #    display.flip()
            #if slow_tick:
            #    c.tick(40)
            """

    def twistedOutside_mainLoopIteration(self):
        self.mainLoopIteration()
        reactor.callLater(.0, self.twistedOutside_mainLoopIteration)

    def twistedOutside_mainLoopIterationDontHandleEvents(self):
        try:
            self.mainLoopIteration(handleEvents=False)
        except:
            traceback.print_exc()
        reactor.callLater(.0, self.twistedOutside_mainLoopIterationDontHandleEvents)

    def runWithTwisted3_TwistedMain(self):
        #for event in pygame.event.get():
        #    if event.type == KEYDOWN:
        #        print event.key
        #    elif event.type == MOUSEBUTTONDOWN:
        #        reactor.callLater(.1, all_done)
        #        return
        reactor.callLater(.0, self.twistedOutside_mainLoopIteration)
        print "*********RUNNING REACTOR"
        reactor.run()

    def grabMouse(self, value):
        self.mouseGrabbed = value
        pygame.mouse.set_visible(not self.mouseGrabbed)

    def toggleMouseGrab(self):
        self.mouseGrabbed = not self.mouseGrabbed
        pygame.mouse.set_visible(not self.mouseGrabbed)

    def updateMouse(self):
        if self.mouseGrabbed:
            pygame.mouse.set_pos(self.width / 2,self.height / 2)

    def quit(self):
        if HaveTwisted:
            if reactor.running:
                reactor.stop()
        else:
            pygame.quit()
        #self._running = 0
        #sys.exit()
       
            


