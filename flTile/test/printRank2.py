import mpi

import sys, os
import traceback
#sys.path = [os.path.join(os.getcwd(), "..") , [os.path.join(os.getcwd(), "..", "..") ] ] + sys.path
#sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path
sys.path = [os.path.join(os.getcwd(),  "..") ] + sys.path
sys.path = [os.path.join(os.getcwd(),  "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.texture import Texture, EasyTexture
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2
from flapp.glDrawUtils import ScreenClearer

from flTile.amConfig import CreateAMConfig
from socket import gethostname, getfqdn

from OpenGL.GL import *
from OpenGL.GLU import *

def run():
    print "starting:", mpi.rank
    os.environ['SDL_VIDEO_WINDOW_POS']="400,300"
    print "Just after run SDL_VIDEO_WIDOW_POS:", mpi.rank, os.environ['SDL_VIDEO_WINDOW_POS']

    rects = [Rect(0,0,1280,1024), Rect(1280,0, 1280,1024)]

    os.environ["DISPLAY"] = ":0.0"
    #os.environ['SDL_VIDEO_WINDOW_POS']="0,0"
    import pygame

    windowWidth = 2560 # 1280# 320
    windowHeight = 1024 # 1024 # 280
    app = App(windowWidth, windowHeight)

    renderers = []
    for i in range(len(rects)):
        displayRect  = rects[i]
        if i == 0:
            renderer = glRenderer2D(multipleRenderers=True, firstRenderer=True)
            renderer.addFrameSetupObj(ScreenClearer(color=(.9, .4, .4), clearDepth=False))
        else:
            renderer = glRenderer2D(multipleRenderers=True)
            renderer.addFrameSetupObj(ScreenClearer(color=(.4, .9, .4), clearDepth=False))
        renderers.append(renderer)
        app.addRenderer(renderer)

    print "app.initialize", mpi.rank
    app.initialize(windowBorder=False)

    for i in range(len(rects)):
        print "SETTING RECT:", rects[i]
        renderers[i].init(app.width, app.height, viewportRect=rects[i])

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
        def __init__(self, imageFilename="../data/test1.png", initialOffset=(0,0) ):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True
            #self.texture = Texture( "../data/test1.png")
            self.easyTexture = EasyTexture(imageFilename, blend=False)
            #self.easyTexture.width = renderer.width * 0.8
            #self.easyTexture.height = renderer.height * 0.8
            self.easyTexture.width = renderer.width
            self.easyTexture.height = renderer.height
            self.useDrawPixel = False # For comparison debugging
            self.useDrawPixel = False # For comparison debugging
            self.xvel = 0.1
            self.yvel = 0.1
            self.easyTexture.zoom(2, 2)
            self.easyTexture.setOffset(initialOffset[0], initialOffset[1])

        def update(self, secs, app):
            self.easyTexture.pan(self.xvel * secs, self.yvel* secs) 

        def draw(self, renderer):
            #glClearColor(.8, .8, .8, 1.0)
            #glClear(GL_COLOR_BUFFER_BIT)
            # glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

            # self.texture.blit( Vec2(10,10), Rect(10,10, 30,30), (app.width, app.height) )
            # self.texture.blit( Vec2(50,50), Rect(0,0, 64,64), (app.width, app.height) )
            # self.texture.blit( Vec2(150,50), Rect(40,40, 64,64), (app.width, app.height) , blend=True)
            #self.texture.blit( Vec2(0.1 * renderer.width,0.1 * renderer.height), Rect(0,0, 30,30), (app.width, app.height) )
            self.easyTexture.draw()

    imageFilename="/home/eolson/am-macs/data/JC4-Sol1355A_1358A_DeckPan_L456atc_br2.jpg"

    glEnable(GL_TEXTURE_2D)
    for i in range(len(renderers)):
        rect = rects[i]
        box = glTxtrBox(imageFilename, initialOffset=(rect.x, rect.y))
        app.addDynamicObject(box, addToRenderer=False)
        renderers[i].addDynamicObject(box)

    print "Running app"
    try:
        app.run()
    except:
        traceback.print_exc()

    #import time
    #time.sleep(3)
    print "exiting: ", mpi.rank


if __name__ == "__main__":
  run()
