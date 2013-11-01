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

    mote.irBasicModeOn()

    return mote


def run():
    windowWidth = 320
    windowHeight = 280
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
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True
            self.points = [ (0.5, 0.5) ]
            self.color = (0.4, 0.4, 0.9)
            self.pointSize = 10 

        def setPointsFromList(self, pointList):
            self.points = pointList

        def update(self, app, secs):
            pass

        def eraseDraw(self, app):
            pass

        def draw(self, renderer):
            glColor3fv(self.color)
            glPointSize(self.pointSize)
            glBegin(GL_POINTS)
            # print "drawing: ", self.points
            for p in self.points:
                glVertex2f(p[0] * renderer.width, p[1] * renderer.height)
            glEnd()

    points = pointListRenderer()
    app.addDynamicObject(points)
    app.drawBounds = 0

    class motePointProcessor:
        def __init__(self, mote, pointsView):
            self.hasDrawFunc=False
            self.mote = mote
            self.pointsView = pointsView

        def draw(self, renderer):
            pass

        def update(self, app, secs):
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

