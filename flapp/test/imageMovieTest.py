import sys, os, traceback
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.texture import Texture, EasyTexture
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2
import random
import string

from OpenGL.GL import *
from OpenGL.GLU import *

from flapp.movie.imageMovieReader import ImageMovieReader
from flapp.movie.glMoviePlayer import GLMoviePlayer

if __name__ == "__main__":
    r = ImageMovieReader()
    if len(sys.argv) > 1:
        r.setPath(sys.argv[1])
    else:
        r.setPath("/home/eolson/testMovieFrames")

    memMapped = False
    if "--preload" in sys.argv:
        memMapped = True
        print "Will Preload."

    r.loadFile(preload=memMapped)

    # Setup window, etc.
    #windowWidth = 1000 # 320
    #windowHeight = 700 # 280
    windowWidth, windowHeight = r.getSize()
    #maxWindowWidth, maxWindowHeight = 1024, 768
    #windowWidth = min(maxWindowWidth, r.getSize()[0])
    #windowHeight = min(maxWindowHeight, r.getSize()[1])

    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight)

    glEnable(GL_TEXTURE_2D)

    p = GLMoviePlayer(origWidth=r.getSize()[0], origHeight=r.getSize()[1])
    p.setPos(0, 0)

    p.setVideoSource(r)
    r.start()
    app.addDynamicObject(p)
    #app.addDynamicObject(r, addToRenderer=False)
    app.printFPS = True

    app.drawBounds = 0

    app.run()

