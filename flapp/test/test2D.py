import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D

from OpenGL.GL import *
from OpenGL.GLU import *

def run():
    windowWidth = 320
    windowHeight = 280
    app = App(windowWidth, windowHeight)
    app.setRenderer(glRenderer2D())
    app.initialize()

    glDisable(GL_DEPTH_TEST)        #use our zbuffer
    glDisable(GL_LIGHTING)        #use our zbuffer
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, windowWidth, 0, windowHeight)
    #gluPerspective(45.0,float(windowWidth/windowHeight).0,0.1,100.0)
    print "after gluOrtho2D"
    glColor3f(0,1,0)
    print "after glColor"

    class glBox:
        def __init__(self):
            self.hasDrawFunc=True
            self.hasEraseDrawFunc=True
            self.visible = True

        def update(self, app, secs):
            pass

        def eraseDraw(self, app):
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

    box = glBox()
    print "after make box"
    app.addDynamicObject(box)
    print "after adddyn"
    app.drawBounds = 0

    app.appDoesCollisionChecks = False
    print "Running app"
    app.run()
    #app.runWithTwisted()


if __name__ == "__main__":
  run()
