import sys, os
import traceback
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path
from random import randrange

import mpi

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.texture import Texture, EasyTexture
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2
from flapp.glDrawUtils import ScreenClearer

from amConfig import CreateAMConfig
from socket import gethostname, getfqdn

from OpenGL.GL import *
from OpenGL.GLU import *

from threading import Lock

from wiitrack.moteCursor import MoteMouse, connectToMote

class TileMote:
    def __init__(self, panningObjects, displayWidth, displayHeight ):
        self.panningObjects = panningObjects
        self.lastX = 0
        self.lastY = 0
        self.queue = []
        if mpi.rank == 0:
            self.dataLock = Lock()
        self.width = displayWidth
        self.height = displayHeight

    def getPos(self):
        return self.lastX, self.lastY

    def setMousePosNormalized(self, x, y):
        print "Tile Mote queuing: ", x, y
        self.dataLock.acquire() # this lock probably isn't necessary
        self.queue.append((x,y))
        self.dataLock.release()

    def syncAndApply(self):
        tmpQueue = None
        if mpi.rank == 0:
            self.dataLock.acquire() # this lock probably isn't necessary

            try:
                tmpQueue = self.queue
                self.queue = []
            except:
                traceback.print_exc()
            finally:
                self.dataLock.release()
 
        if mpi.rank == 0 and len(tmpQueue) > 0:
            print "Bcasting:", tmpQueue
        #print "mpi barrier", mpi.rank
        #mpi.barrier()
        #print "bcast:", mpi.rank
        if mpi.rank == 0:
            resultQueue = mpi.bcast(tmpQueue)
        else:
            resultQueue = mpi.bcast()

        if len(resultQueue) > 0:
            print "Bcasting recv:", resultQueue, mpi.rank

        for panningObj in self.panningObjects:
            for result in resultQueue:
                x = int((result[0] - self.lastX) * self.width)
                y = int((result[1] - self.lastY) * self.height)
                print "panning, ", mpi.rank, ":", x, y
                panningObj.pan( x, y)
                self.lastX = result[0]
                self.lastY = result[1]

def run():
   
    tileConfig = CreateAMConfig()
    # fqdn = getfqdn()
    hostname = gethostname()
    machineDesc = tileConfig.getMachineDescByHostname(hostname)
 
    localRects = []
    absoluteRects = []
    for tile in machineDesc.tiles:
        localRects.append(tileConfig.getLocalDrawRect(tile.uid))
        absoluteRects.append(tileConfig.getAbsoluteFullDisplayRect(tile.uid))

    print hostname, machineDesc.hostname, localRects, absoluteRects
    # return

    fullRect = tileConfig.getMainDisplayRect()
    if mpi.rank == 0:
        print "FULL DISPLAY:", fullRect.width, fullRect.height
    
    #rects = [Rect(0,0,1280,1024), Rect(1280,0, 1280,1024)]
    #rects = [Rect(0,0,1280,1024)]

    os.environ["DISPLAY"] = ":0.0"
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

    imageFilename = sys.argv[1]

    #windowWidth = 2560 # 1280# 320
    #windowWidth = 3840 # 1280# 320
    windowWidth = 2560 # 1280# 320
    windowHeight = 1024 # 1024 # 280
    #windowWidth = 1280 # 1280# 320
    #windowHeight = 1024 # 1024 # 280
    app = App(windowWidth, windowHeight)

    renderers = []
    for i in range(len(localRects)):
        displayRect  = localRects[i]
        if i == 0:
            renderer = glRenderer2D(multipleRenderers=True, firstRenderer=True)
            renderer.addFrameSetupObj(ScreenClearer(color=(.9, .4, .4), clearDepth=False))
        else:
            renderer = glRenderer2D(multipleRenderers=True)
            renderer.addFrameSetupObj(ScreenClearer(color=(.4, .9, .4), clearDepth=False))
        renderers.append(renderer)
        app.addRenderer(renderer)

    app.initialize(windowBorder=False)
    #app.initialize(windowBorder=True)

    for i in range(len(localRects)):
        print "SETTING RECT:", localRects[i]
        renderers[i].init(app.width, app.height, viewportRect=localRects[i])

    class glBox:
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True

        def update(self, app, secs):
            pass

        def draw(self, renderer):
            #glClearColor(.4, .4, .4, 1.0)
            #glClear(GL_COLOR_BUFFER_BIT)
            glBegin(GL_TRIANGLE_STRIP)
            glVertex2f(100, 200)
            glVertex2f(100, 100)
            glVertex2f(200, 200)
            glVertex2f(200, 100)
            glEnd()

    class glTxtrBox:
        def __init__(self, imageFilename, screenRect, fullRect, absRect, initialOffset=(0,0), zoom=(4,4), imagePos=(0,0), imageSize=None ):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True
            self.texture = Texture( imageFilename)
            #self.easyTexture = EasyTexture(imageFilename, screenGeomRect=screenRect, blend=False)
            #self.easyTexture.width = renderer.width * 0.8
            #self.easyTexture.height = renderer.height * 0.8
            #self.easyTexture.width = renderer.width
            #self.easyTexture.height = renderer.height
            self.useDrawPixel = False # For comparison debugging
            self.xvel = 0.1
            self.yvel = 0.1
            self.zoom = zoom
            #self.easyTexture.zoom(zoom[0], zoom[1])
            #self.easyTexture.setOffset(initialOffset[0], initialOffset[1])
            self.autoPan = True
            self.imagePos = Vec2(imagePos[0], imagePos[1])
            if imageSize == None:
                self.imageSize = self.texture.getWidth(), self.texture.getHeight()
            else:
                self.imageSize = imageSize
            self.fullRect = fullRect
            self.absRect = absRect
            self.screenRect = screenRect

        def getPos(self):
            return (self.imagePos.x, self.imagePos.y)

        def setPos(self, x, y):
            self.imagePos = Vec2(x,y)

        def update(self, secs, app):
            pass
            #if self.autoPan:
            #    self.easyTexture.pan(self.xvel * secs, self.yvel* secs) 

        def pan(self, xchange, ychange):
            if mpi.rank == 1:
                print "Panning:", xchange, ychange
            #self.easyTexture.pan(xchange * 300, ychange * 300)

        def draw(self, renderer):
            #glClearColor(.8, .8, .8, 1.0)
            #glClear(GL_COLOR_BUFFER_BIT)
            # glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

            # self.texture.blit( Vec2(10,10), Rect(10,10, 30,30), (app.width, app.height) )
            # self.texture.blit( Vec2(50,50), Rect(0,0, 64,64), (app.width, app.height) )
            # self.texture.blit( Vec2(150,50), Rect(40,40, 64,64), (app.width, app.height) , blend=True)
            #self.texture.blit( Vec2(0.1 * renderer.width,0.1 * renderer.height), Rect(0,0, 30,30), (app.width, app.height) )

            # convert to local coords
            localBtmLeft = Vec2(self.imagePos.x - self.absRect.x, self.imagePos.y - self.absRect.y)
            localTopRight = Vec2(localBtmLeft.x + self.imageSize[0], localBtmLeft.y + self.imageSize[1])
            # clip to max/min of local display
            localBtmLeft = Vec2(max(localBtmLeft.x, 0), max(localBtmLeft.y, 0))
            #if mpi.rank == 3:
            #    print "clip top right y:", localTopRight.y, self.screenRect.height
            localTopRight = Vec2(min(localTopRight.x, self.screenRect.width), min(localTopRight.y, self.screenRect.height))
            #if mpi.rank == 3:
            #    print "clip top right y:", localTopRight.y
            blitSize = Vec2(localTopRight.x - localBtmLeft.x, localTopRight.y - localBtmLeft.y)

            # convert clipped local coords back to global coords find the source rect
            globalBtmLeft = Vec2(localBtmLeft.x + self.absRect.x, localBtmLeft.y + self.absRect.y)
            globalTopRight = Vec2(localTopRight.x + self.absRect.x, localTopRight.y + self.absRect.y)

            # convert global coords to txtr coords
            offset = Vec2(globalBtmLeft.x - self.imagePos.x , globalBtmLeft.y - self.imagePos.y)
            #size = (globalTopRight.x - globalBtmLeft.x, globalTopRight.y - globalBtmLeft.y + 80)
            size = (globalTopRight.x - globalBtmLeft.x, localTopRight.y - localBtmLeft.y)
            if size[0] > 0 and size[1] > 0:
                #if mpi.rank == 3:
                #    print "renderer height:", renderer.height
                self.texture.blit( localBtmLeft, Rect(offset.x,offset.y, size[0], size[1]), (renderer.width, renderer.height) )

            #self.easyTexture.draw()

    #box = glBox()
    #app.addDynamicObject(box)
    glEnable(GL_TEXTURE_2D)
    boxes = []
    for i in range(len(renderers)):
        absRect = absoluteRects[i]
        locRect = localRects[i]
        renderer = renderers[i]
        box = glTxtrBox(imageFilename, screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(2000,500), absRect= absRect, fullRect=fullRect)

        # to scale, change the geometry and the txtr coords: imageSize and
        #box.imageSize = (box.imageSize[0]*2, box.imageSize[1]*2)

        #box.easyTexture.zoom(5,1)

        #box.easyTexture.setOffset( (absRect.x % float(box.easyTexture.getWidth())) / box.easyTexture.getWidth(),
        #                           (absRect.y % float(box.easyTexture.getHeight())) / box.easyTexture.getHeight() )

        # box.easyTexture.setWidth( float(locRect.width) / float(box.easyTexture.getHeight()) )

        #zoom = (0.5,1)
        #box.easyTexture.setZoom(zoom[0], zoom[1])
        #box.easyTexture.setOffset(absRect.x * zoom[0] ,absRect.y * zoom[1])
        #box.easyTexture.setZoom(float(box.easyTexture.getWidth()) / localRect.width,
        #                        float(box.easyTexture.getHeight()) / localRect.height )
        # scale offset back by zoom   (offset is between 0 and 1)
        #box.easyTexture.setOffset( float(rect.x) / fullRect.width * box.easyTexture.getWidth(),
        #                           float(rect.y) / fullRect.height * box.easyTexture.getHeight())

        app.addDynamicObject(box, addToRenderer=False)
        renderers[i].addDynamicObject(box)
        boxes.append(box)

    app.drawBounds = 0

    # setup control
    def setupMoteControl(panningObjects, app, displayWidth, displayHeight):
        tileMote = TileMote(panningObjects, displayWidth, displayHeight)
        if mpi.rank == 0:
            mote = connectToMote()
            moteMouse = MoteMouse(mote,tileMote)
        else:
            moteMouse = None
            mote = None

        """
        class MouseUpdater:
            def __init__(self, moteMouse, tileMote):
                self.moteMouse = moteMouse
                self.tileMote = tileMote

            def update(self, app, secs):
                # process data from device
                if mpi.rank == 0:
                    self.moteMouse.processAndUpdateMouse()
                # send data to all nodes and apply
                self.tileMote.syncAndApply()

        app.addDynamicObject(MouseUpdater(moteMouse, tileMote), addToRenderer=False)
        """

        return mote, moteMouse, tileMote

    mote = None

    for arg in sys.argv:
        if "wii" in arg.lower():
            mote, moteMouse, tileMote = setupMoteControl(boxes, app, fullRect.width, fullRect.height)
            for box in boxes:
                box.autoPan=False
            break  # break out of this loop

    class Syncer:
        def __init__(self, cursorObjectsListList=None):
            # list of objects to sync to list of positions:  [ [a1,a2,a3], [b1,b2] ]
            #  
            # access: cursor[i][localcopies]
            # only the first object for each cursors is read, all are written
            if cursorObjectsListList == None:
                self.cursorObjects = []
            else:
                self.cursorObjects = cursorObjectsListList

            self.cursors = []
            for obj in self.cursorObjects:
                self.cursors.append( (0,0) )

            self.resultCursors = []
            if mpi.rank == 0:
                self.dataLock = Lock()

        def update(self, app, secs):
            self.syncAndApply()

        def syncAndApply(self):
            if mpi.rank == 0:
                self.dataLock.acquire() # this lock probably isn't necessary yet

                try:
                    for i in range(len(self.cursorObjects)):
                        self.cursors[i] = self.cursorObjects[i][0].getPos()

                except:
                    traceback.print_exc()
                finally:
                    self.dataLock.release()
 
            if mpi.rank == 0:
                resultCursors = mpi.bcast(self.cursors)
            else:
                self.resultCursors = mpi.bcast()

            if mpi.rank != 0:
                for i in range(len(self.cursorObjects)):
                    if len(self.resultCursors) > i:
                        # access: cursorObjects[i][localcopies]
                        for j in range(len(self.cursorObjects[i])): # set for each local copy
                            self.cursorObjects[i][j].setPos( self.resultCursors[i][0], self.resultCursors[i][1])

            #if len(resultQueue) > 0:
            #    print "Bcasting recv:", resultQueue, mpi.rank

    class CursorAutoMover:
        def __init__(self, target, xrange=(0,5000), yrange=(0,3000), xvel=100, yvel=100):
            self.target = target
            self.xvel = xvel
            self.yvel = yvel
            self.xrange  = xrange
            self.yrange  = yrange
            self.visible = False

        def draw(self):
            pass

        def update(self, secs, app):
            posTuple = self.target.getPos()
            pos = Vec2(posTuple[0], posTuple[1])
            pos.x = pos.x + self.xvel * secs
            pos.y = pos.y + self.yvel * secs
            if pos.x > self.xrange[1]:
                self.xvel = -abs(self.xvel)
            if pos.y > self.yrange[1]:
                self.yvel = -abs(self.yvel)

            if pos.x < self.xrange[0]:
                self.xvel = abs(self.xvel)
            if pos.y < self.xrange[0]:
                self.yvel = abs(self.yvel)

            self.target.setPos(pos.x, pos.y)
            # print "pos:", pos.x, pos.y

    #class Cursor:
    def CreateCursor(x=500,y=500, xvel=100, yvel=100):
        tmpCursors = []
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            cursor = glTxtrBox("../../../data/fl-logo-color-small.gif", screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(x,y), absRect= absRect, fullRect=fullRect)
    
            app.addDynamicObject(cursor, addToRenderer=False)
            renderers[i].addDynamicObject(cursor)
            tmpCursors.append(cursor)
    
            # change this to only happen on master and sync
            if mpi.rank == 0:
                app.addDynamicObject(CursorAutoMover(cursor, xrange=(0, fullRect.width), yrange=(0, fullRect.height), xvel=xvel, yvel=yvel), addToRenderer=False)
        return tmpCursors

    numCursors = 3 
    cursorListList = []
    for i in range(numCursors): 
        nodeCursors = CreateCursor(x=randrange(0,fullRect.width), y=randrange(0,fullRect.height),
                     xvel=randrange(200,400), yvel=randrange(200,400))
        cursorListList.append(nodeCursors)

    # print mpi.rank, " cursor list:", cursorListList
    syncer = Syncer(cursorListList)
    app.addDynamicObject(syncer, addToRenderer=False)


    print "Running app"

    try:
        app.run()
    except:
        traceback.print_exc()
    finally:
        if mpi.rank == 0:
            if mote != None:
                mote.disconnect()
                if mote.readThread != None:
                    print "Exiting, joining thread"
                    mote.readThread.join()



if __name__ == "__main__":
  run()
