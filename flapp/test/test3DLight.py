import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer3D import glRenderer3D
from flapp.pmath.vec3 import Vec3
from flapp.light import Light

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GLUT

class glInitObj:
    def draw(self):
        glEnable(GL_DEPTH_TEST)

class ScreenClearer:
    def draw(self, renderer):
        glClearColor(.5,.8,0.5,0.)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def run():
    windowWidth = 320
    windowHeight = 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer3D()
    renderer.camera.setPos(5, 5, 10)
    renderer.addGlSetupObj(glInitObj())
    renderer.addFrameSetupObj(ScreenClearer())
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight)

    class glSphere:
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True

        def update(self, app, secs):
            pass

        def eraseDraw(self, app):
            pass

        def draw(self, renderer):
            #glClearColor(.8, .8, .8, 1.0)
            #glClear(GL_COLOR_BUFFER_BIT)
            glColor3f(1.0, 0, 0)
            GLUT.glutSolidSphere(2, 16, 16)

    sphere = glSphere()
    print "after make sphere"
    app.addDynamicObject(sphere)

    light = Light(Vec3(5,100,5), 0)
    renderer.addFrameSetupObj(light)

    app.drawBounds = 0

    app.appDoesCollisionChecks = False
    print "Running app"
    # app.printFPS = True
    app.run()
    #app.runWithTwisted()


if __name__ == "__main__":
  run()
