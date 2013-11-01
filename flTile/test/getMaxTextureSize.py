import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.texture import Texture, EasyTexture
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2

from OpenGL.GL import *
from OpenGL.GLU import *

def CheckSpecificTextureSize(width, height, level=0, internalFormat=GL_RGBA, border=0, format=GL_RGBA, type=GL_UNSIGNED_BYTE):
    glTexImage2D(GL_PROXY_TEXTURE_2D, level, internalFormat,  width, height, border, format, type, None);  
    width = glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D, 0, GL_TEXTURE_WIDTH);
    if (width==0): # Can't use that texture
        return False
    else:
        return True

def run():
    windowWidth = 1000# 320
    windowHeight = 800 # 280
    app = App(windowWidth, windowHeight)
    renderer = glRenderer2D()
    app.setRenderer(renderer)
    app.initialize()

    renderer.init(windowWidth, windowHeight) 

    #GLint texSize; glGetIntegerv(GL_MAX_TEXTURE_SIZE, &texSize);  
    print
    print "Max Texture Size:", glGetIntegerv(GL_MAX_TEXTURE_SIZE);
    print

    print "Check specific: 4096x4096, GL_RGBA:", CheckSpecificTextureSize(width=4096, height=4096, internalFormat=GL_RGB)
    print "Check specific: 4097x4096, GL_RGBA:", CheckSpecificTextureSize(width=4097, height=4096, internalFormat=GL_RGBA)
    print "Check specific: 4097x4096, GL_L:", CheckSpecificTextureSize(width=4097, height=4096, internalFormat=GL_LUMINANCE)
    print

    #app.drawBounds = 0

    #print "Running app"
    #app.run()


if __name__ == "__main__":
  run()
