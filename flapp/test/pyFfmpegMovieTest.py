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

from flapp.movie.pyFfmpegMovieReader import PyFfmpegMovieReader
from flapp.movie.glMoviePlayer import GLMoviePlayer

if __name__ == "__main__":
    r = PyFfmpegMovieReader()
    #r.loadFile("/home/eolson/Desktop/jai-head2.mp4")
    #r.setFile("/home/eolson/fl/notes/viz/tomo1.mpg")
    if len(sys.argv) > 1:
        r.setFile(sys.argv[1])
    else:
        r.setFile("/home/eolson/blah_mpeg1.mpg")

    # Note: Example to encode an mpeg1 file readable by pygame.Movie:
    # mencoder original.avi -of mpeg -mpegopts format=mpeg1:tsaf:muxrate=2000 -o test.mpg -srate 44100 -af lavcresample=44100 -oac twolame -twolameopts br=160 -ovc lavc -lavcopts vcodec=mpeg1video:vbitrate=1152:keyint=15:mbd=2

    # Setup window, etc.
    windowWidth = 1000 # 320
    windowHeight = 700 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight)

    glEnable(GL_TEXTURE_2D)

    r.loadFile()
    p = GLMoviePlayer(origWidth=r.getSize()[0], origHeight=r.getSize()[1])
    #p.setPos(50, 200)
    p.setPos(50, 0)
    #p.setPos(50, -50)

    p.setVideoSource(r)
    r.start()
    app.addDynamicObject(p)
    #app.addDynamicObject(r, addToRenderer=False)

    app.drawBounds = 0

    app.run()

