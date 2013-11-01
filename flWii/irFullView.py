import time, sys, os
from mote import detectAllPossible
from moteCache import MoteCache
import traceback

sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path
from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.glDrawUtils import ScreenClearer

from OpenGL.GL import *
from OpenGL.GLU import *

def connectToMote():
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()
    allDevs = detectAllPossible()

    selectedMoteId = None
    for d in allDevs:
        if d in cache.getMotes():
            selectedMoteId = d
            break

    if selectedMoteId == None:
        print "No motes found.  Device ids:", allDevs, "cacheMoteIds:", cache.getMotes().keys()
        sys.exit()

    # mote = cache.getMotes().values()[0]
    mote = cache.getMotes()[selectedMoteId]
    mote.connect()

    mote.setLeds(1,0,0,0)

    mote.startReadThread()

    mote.irFullModeOn()

    return mote


def run():
    windowWidth = 1024 / 2 # 320
    windowHeight = 768 /2 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize()
    renderer.init(windowWidth, windowHeight)

    renderer.addFrameSetupObj(ScreenClearer( (0.8, 0.8, 0.8), clearDepth=False))

    """
    glDisable(GL_DEPTH_TEST)        #use our zbuffer
    glDisable(GL_LIGHTING)        #use our zbuffer
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, windowWidth, 0, windowHeight)
    glColor3f(1,1,0)
    """

    class pointListRenderer:
        M_BASIC = 0
        M_EXT = 1
        M_FULL = 2
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True
            self.points = [ (0.5, 0.5) ]
            self.pointsAndSize = [ (0.5, 0.5, 1.0) ]
            self.pointsFull = [ (0.5, 0.5, 1.0, 0.40, 0.45, 0.60, 0.55, 1.0) ]
            self.color = (0.4, 0.4, 0.9)
            self.lineColor = (0.4, 0.9, 0.4)
            self.pointSize = 10 
            self.lineWidth = 2 
            self.mode = self.M_BASIC

        def setPointsFromList(self, pointList):
            self.points = pointList

        def setPointsAndSizeFromList(self, pointList):
            self.pointsAndSize = pointList

        def setPointsFullFromList(self, pointList):
            self.pointsFull = pointList

        def update(self, app, secs):
            pass

        def eraseDraw(self, app):
            pass

        def draw(self, renderer):
            glColor3fv(self.color)
            if self.mode == self.M_BASIC:
                glPointSize(self.pointSize)
                glBegin(GL_POINTS)
                # print "drawing: ", self.points
                for p in self.points:
                    glVertex2f(p[0] * renderer.width, p[1] * renderer.height)
                glEnd()
            elif self.mode == self.M_EXT:
                # print "drawing: ", self.points
                for p in self.pointsAndSize:
                    glPointSize(self.pointSize * (p[2] + 0.5))
                    glBegin(GL_POINTS)
                    glVertex2f(p[0] * renderer.width, p[1] * renderer.height)
                    glEnd()
            elif self.mode == self.M_FULL:
                glColor3fv(self.color)
                for p in self.pointsFull:
                    glPointSize(self.pointSize * (p[7] + 0.5))
                    glBegin(GL_POINTS)
                    glVertex2f(p[0] * renderer.width, p[1] * renderer.height)
                    glEnd()
                glColor3fv(self.lineColor)
                for p in self.pointsFull:
                    glLineWidth(self.lineWidth * (p[7] + 0.5))
                    glBegin(GL_LINE_LOOP)
                    glVertex2f(p[3] * renderer.width, p[4] * renderer.height)
                    glVertex2f(p[5] * renderer.width, p[4] * renderer.height)
                    glVertex2f(p[5] * renderer.width, p[6] * renderer.height)
                    glVertex2f(p[3] * renderer.width, p[6] * renderer.height)
                    glEnd()
            else:
                raise Exception("Unimplemented pointList draw mode" + str(self.mode))

    points = pointListRenderer()
    app.addDynamicObject(points)
    app.drawBounds = 0

    class motePointProcessor:
        def __init__(self, mote, pointsView):
            self.hasDrawFunc=False
            self.mote = mote
            self.pointsView = pointsView
            if mote.irMode == "f":
                self.pointsView.mode = self.pointsView.M_FULL
            elif mote.irMode == "e":
                self.pointsView.mode = self.pointsView.M_EXT
            else: # mote.irMode == "b":
                self.pointsView.mode = self.pointsView.M_BASIC

        def draw(self, renderer):
            pass

        def update(self, app, secs):
            if self.mote.irMode == "f":
                points = self.mote.extractNormalizedPointsFull()
                if len(points) > 0:
                    # print "setting points:", points[-1]
                    self.pointsView.setPointsFullFromList(points[-1])
            elif self.mote.irMode == "e":
                points = self.mote.extractNormalizedPointsAndSize()
                if len(points) > 0:
                    # print "setting points:", points[-1]
                    self.pointsView.setPointsAndSizeFromList(points[-1])
            else: # irMode == "b" 
                points = self.mote.extractNormalizedPoints()
                if len(points) > 0:
                    # print "setting points:", points[-1]
                    self.pointsView.setPointsFromList(points[-1])

    mote = connectToMote()
    # mote = None

    processor = motePointProcessor(mote, points)
    app.addDynamicObject(processor)

    print "Running app"
    try:
        app.run()
    except:
        traceback.print_exc()
    finally:
        mote.disconnect()
        if mote.readThread != None:
            print "Exiting, joining thread"
            mote.readThread.join()


if __name__ == "__main__":
    run()

