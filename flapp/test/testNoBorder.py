import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.texture import Texture, EasyTexture
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2

from OpenGL.GL import *
from OpenGL.GLU import *

def run():
    windowWidth = 1000# 320
    windowHeight = 800 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize(windowBorder=False)

    renderer.init(windowWidth, windowHeight) 

    class glBox:
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True

        def update(self, app, secs):
            pass

        def draw(self, renderer):
            glClearColor(.8, .8, .8, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)
            glBegin(GL_TRIANGLE_STRIP)
            glVertex2f(100, 200)
            glVertex2f(100, 100)
            glVertex2f(200, 200)
            glVertex2f(200, 100)
            glEnd()

    class glTxtrBox:
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True
            #self.texture = Texture( "../data/test1.png")
            self.easyTexture = EasyTexture( "../data/test1.png")
            self.easyTexture.width = renderer.width * 0.8
            self.easyTexture.height = renderer.height * 0.8
            self.useDrawPixel = False # For comparison debugging

        def update(self, app, secs):
            pass

        def draw(self, renderer):
            #glClearColor(.8, .8, .8, 1.0)
            #glClear(GL_COLOR_BUFFER_BIT)
            # glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

            # self.texture.blit( Vec2(10,10), Rect(10,10, 30,30), (app.width, app.height) )
            # self.texture.blit( Vec2(50,50), Rect(0,0, 64,64), (app.width, app.height) )
            # self.texture.blit( Vec2(150,50), Rect(40,40, 64,64), (app.width, app.height) , blend=True)
            #self.texture.blit( Vec2(0.1 * renderer.width,0.1 * renderer.height), Rect(0,0, 30,30), (app.width, app.height) )
            self.easyTexture.draw()

    box = glBox()
    app.addDynamicObject(box)
    glEnable(GL_TEXTURE_2D)
    box2 = glTxtrBox()
    app.addDynamicObject(box2)

    app.drawBounds = 0

    print "Running app"
    app.run()


if __name__ == "__main__":
  run()
