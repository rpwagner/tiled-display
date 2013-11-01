# Test that plays back two movies at once.
# Note: pygame movie reader accepts a very limited number of
#  formats.  See other tests for alternative movei readers.

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

from flapp.movie.pygameMovieReader import PygameMovieReader
from flapp.movie.glMoviePlayer import GLMoviePlayer

if __name__ == "__main__":
    r = PygameMovieReader()
    #r.loadFile("/home/eolson/Desktop/jai-head2.mp4")
    #r.setFile("/home/eolson/fl/notes/viz/tomo1.mpg")
    moviePath = "/home/eolson/blah_mpeg1.mpg"
    if len(sys.argv) > 1:
        moviePath = sys.argv[1]
    r.setFile(moviePath)

    # Note: Example to encode an mpeg1 file readable by pygame.Movie:
    # mencoder original.avi -of mpeg -mpegopts format=mpeg1:tsaf:muxrate=2000 -o test.mpg -srate 44100 -af lavcresample=44100 -oac twolame -twolameopts br=160 -ovc lavc -lavcopts vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2

    # Setup window, etc.
    windowWidth = 1000# 320
    windowHeight = 800 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight)

    glEnable(GL_TEXTURE_2D)

    r.loadFile()
    p = GLMoviePlayer(origWidth=r.getSize()[0], origHeight=r.getSize()[1])
    p.setPos(50, 300)

    p.setVideoSource(r)
    r.start()
    app.addDynamicObject(p)
    #app.addDynamicObject(r, addToRenderer=False)

    # second movie
    r2 = PygameMovieReader()
    moviePath2 = "/home/eolson/blah_mpeg1.mpg"
    if len(sys.argv) > 2:
        moviePath2 = sys.argv[2]
    r2.setFile(moviePath2)
    r2.loadFile()
    p2 = GLMoviePlayer(origWidth=r2.getSize()[0], origHeight=r2.getSize()[1])
    p2.setVideoSource(r2)
    p2.setPos(100, -500)
    r2.start()
    app.addDynamicObject(p2)

    app.drawBounds = 0

    app.run()

