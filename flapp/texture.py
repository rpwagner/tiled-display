# Univesity of Chicago,
# Feb 2, 2008
# Eric Olson
# adapted from home version written by Eric.

import Image
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
import pygame
import traceback

from flapp.pmath.vec2 import Vec2
from flapp.pmath.rect import Rect

from flapp.glDrawUtils import DrawTxtrd2dSquareIn2DFromCorner, Draw2dSquareIn2D
from flapp.utils.utils import clamp

M_NONE=0
M_DEFAULT=1
M_REPLACE=2
M_DECAL=3
M_MODULATE=4
M_ADD=5
M_BLEND=6
GLTextureModes = {M_NONE:None,
                          M_DEFAULT:GL_REPLACE,
                          M_REPLACE:GL_REPLACE,
                          M_DECAL:GL_DECAL,
                          M_MODULATE:GL_MODULATE,
                          M_ADD:GL_ADD,
                          M_BLEND:GL_BLEND
                         }

BlendFuncList = [
            (None, None),
            (GL_SRC_ALPHA, GL_ONE),
            (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
             ]

#Utility functions
def getAlphaImageFromImageColor(image):
    imL = Image.new("L", image.size)
    for i in range(image.size[0]):
        for j in range(image.size[0]):
            # I know, this line is too long
            imL.putpixel( (i,j), int(round(sum( image.getpixel((i,j))[:3] ) / 3.0 )))
            #imL.putpixel( (i,j), 255 -(round( sum( image.getpixel((i,j))[:3] ) / 3.0 )))
            #imL.putpixel( (i,j), 255)
    return imL

def pilMaxSize(image, maxSize, method = 3):
    """ im = maxSize(im, (maxSizeX, maxSizeY), method = Image.BICUBIC)

    Resizes a PIL image to a maximum size specified while maintaining
    the aspect ratio of the image.  Similar to Image.thumbnail(), but allows
    usage of different resizing methods and does NOT modify the image in
place."""
    if image.size[0] <= maxSize[0] and image.size[1] <= maxSize[1]:
        return image

    imAspect = float(image.size[0])/float(image.size[1])
    outAspect = float(maxSize[0])/float(maxSize[1])

    if imAspect >= outAspect:
        #set to maxWidth x maxWidth/imAspect
        return image.resize((maxSize[0], int((float(maxSize[0])/imAspect) +
0.5)), method)
    else:
        #set to maxHeight*imAspect x maxHeight
        return image.resize((int((float(maxSize[1])*imAspect) + 0.5),
maxSize[1]), method)


class Texture:
    def loadL(self):
        #ix, iy, self.image = image.size[0], image.size[1], image.tostring("raw", "L", 0, -1)
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "L", 0, -1)
        self.numChannels = 1

    def loadLA(self):
        #ix, iy, self.image = image.size[0], image.size[1], image.tostring("raw", "L", 0, -1)
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "LA", 0, -1)
        self.numChannels = 2

    def loadRGBA(self):
        #ix, iy, self.image = image.size[0], image.size[1], image.tostring("raw", "RGBA", 0, -1)
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "RGBA", 0, -1)
        self.numChannels = 4

    def loadRGBX(self):
        print "Load RGBX worked (?) **********"
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "RGBX", 0, -1)
        self.numChannels = 4

    def loadRGB(self):
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "RGB", 0, -1)
        self.numChannels = 3


    def setAlpha(self, mode):
        # convert wasn't quite right
        #imL = self.image.convert("L")
        imL = getAlphaImageFromImageColor(self.image)
        if self.image.mode == "RGB":
            self.image = self.image.convert("RGBA")

        if mode == 0:             # do nothing, all white
            self.image.putalpha(255)
        elif mode == 1:           # Black Color is invisible
            print "*****PERFORMANCE/MEM WARNING, this should be implemented with masks"
 
            for i in range(self.image.size[0]):
                for j in range(self.image.size[j]):
                    if self.image.getpixel( (i,j) )[:3] == (0,0,0):
                        px = self.image.getpixel( (i,j) )[:3]
                        px = (px[0], px[1], px[2], 0)
                        self.image.putpixel( (i,j), px)
            # A better way would involve this:  Look at rgbimagetest.py and
            #   http://www.pythonware.com/library/pil/handbook/introduction.htm  
            #mask0 = source[0].point(lambda i: i == 0)
            #mask1 = source[1].point(lambda i: i == 0)
            #mask2 = source[2].point(lambda i: i == 0)
        elif mode == 2:           # gradual invisibility, just set alpha
            source = self.image.split()
            source[3].paste(imL)
            self.image = Image.merge("RGBA", source)
        elif mode == 3:           # gradual invisibility, also set RGB to white
            print "*****PERFORMANCE/MEM WARNING, this should be implemented as LA, not RGBA"
            source = self.image.split()
            source[3].paste(imL)
            tmpWhiteL = Image.new("L", (self.image.size[0], self.image.size[1]), (1) )
            source[0].paste(tmpWhiteL)
            source[1].paste(tmpWhiteL)
            source[2].paste(tmpWhiteL)
            self.image = Image.merge("RGBA", source)

        print "After load alpha, alpha values:",
        dataStr = self.image.tostring("hex")
        channel = 3
        for i in range(channel, self.image.size[0] * self.image.size[1] * 4):
            print "%s%s" % (dataStr[i*2], dataStr[i*2+1]),
        print

        self.imagestr = self.image.tostring("raw")
        self.numChannels = 4

    def loadRGBSetAlpha(mode):
        ix, iy, self.imagestr = self.image.size[0], self.image.size[1], self.image.tostring("raw", "RGB", 0, -1)
        self.numChannels = 3
        self.setAlpha(mode)

    def __init__(self, filename, maxWidthHeight = None, cropRect=None):
        self.filename = filename
        if filename != None and len(filename) > 0:
            print "texture loading: ", filename
            self.image = Image.open(filename) 
            # maxWidthHeight = (4096,4096)
            print "CROP RECT:", filename, cropRect
            if cropRect != None:
                # pil crop: box is a 4-tuple defining the
                # left, upper, right, and lower pixel coordinate.
                self.image = self.image.crop( (cropRect.x, cropRect.y, cropRect.x+cropRect.width, cropRect.y+cropRect.height) )
                print "CROPPED 1:", self.image.size
                # Next line is probably optional:
                # crop is a lazy operation. Changes to the source image may or may not be reflected in the cropped image. To get a separate copy, call the load method on the cropped copy.
                #self.image.load() # copy the cropped region.
            if maxWidthHeight != None:
                self.image = pilMaxSize(self.image, maxWidthHeight)

            # self.image = image.transpose(Image.FLIP_TOP_BOTTOM)
            self.numChannels = None
            # print "Info:", self.image.info
     
            # convert gifs, etc. to rgb or rgba before using.
            if self.image.mode == "P":
                self.image = self.image.convert("RGBA") 

            # print dir(Image.core)
            # print dir(Image.core.raw_encoder)
            try:
                if self.image.mode == "L":
                    self.loadL()
                elif self.image.mode == "LA":
                    self.loadLA()
                else:
                    self.loadRGBA()
                # self.loadRGBX()
            except SystemError, e:
                print e

                #try:
                #    self.loadRGBX()
                #except SystemError, e:
                #    print e
                self.loadRGB()

            print "Loaded.  num channels:", self.numChannels, "size:", self.image.size
            self.size = self.image.size
        else:
            self.size = (1,1)
            self.numChannels = 4
            self.image = Image.new("RGBA", self.size)
            self.imagestr = self.image.tostring("raw", "RGB", 0, -1)


        self.glId = glGenTextures(1)
        if self.glId == 0:
            raise Exception("Invalid gl id")
        self.initialLoad()
        """
        from binascii import hexlify
        print "imagestr len:", len(self.imagestr)
        print "First pixels:",
        for i in range(4):
            print hexlify(self.imagestr[i]),
        if len(self.imagestr) > 8324:
            print
            for i in range(8320, 8324):
                print hexlify(self.imagestr[i]),
            print
        # print hexlify(self.imagestr)  # 32768
        """

    def reloadGLTextureFromData(self):
        self.bind()
        if 4 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.size[0], self.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns

        elif 3 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.size[0], self.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        elif 2 == self.numChannels:
            #print "glTexImage2D: GL_LUMINANCE_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, self.size[0], self.size[1], 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        elif 1 == self.numChannels:
            #print "glTexImage2D: GL_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.size[0], self.size[1], 0, GL_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        else:
            print "texture.py: numchannels not handled.", self.numChannels
            raise Exception("Invalid num channels")

        self.unbind()

    def setSize(self, size, numChannels=None):
        self.size = (size[0], size[1])
        if numChannels:
            self.numChannels = int(numChannels)
        if self.numChannels == 4:
            self.image = Image.new("RGBA", self.size)
            self.imagestr = self.image.tostring("raw", "RGBA", 0, -1)
        else:
            self.image = Image.new("RGB", self.size)
            self.imagestr = self.image.tostring("raw", "RGB", 0, -1)

    def initialLoad(self):
        self.bind()
        glPixelStoref(GL_UNPACK_ALIGNMENT, 1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR);
        #  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_NEAREST_MIPMAP_NEAREST);

        #print "image size:", self.image.size
        #print "num Channels:", self.numChannels
        if 4 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.image.size[0], self.image.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns

        elif 3 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image.size[0], self.image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        elif 2 == self.numChannels:
            print "glTexImage2D: GL_LUMINANCE_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, self.image.size[0], self.image.size[1], 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        elif 1 == self.numChannels:
            print "glTexImage2D: GL_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.image.size[0], self.image.size[1], 0, GL_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        else:
            print "texture.py: numchannels not handled.", self.numChannels
            raise Exception("Invalid num channels")
        

         # gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, txtr->GetColumns(), txtr->GetRows(),
        #     GL_RGBA, GL_UNSIGNED_BYTE, (uchar*) txtr->GetDataPtrUchar());


        self.unbind()

    def getWidth(self):
        #return self.image.size[0]
        return self.size[0]

    def getHeight(self):
        #return self.image.size[1]
        return self.size[1]

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.glId);
        # print "glId:", self.glId

    def rawTex(self):
        if 4 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.image.size[0], self.image.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns

        elif 3 == self.numChannels:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image.size[0], self.image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tostring()); #  width == columns
        elif 2 == self.numChannels:
            print "glTexImage2D: GL_LUMINANCE_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, self.image.size[0], self.image.size[1], 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        elif 1 == self.numChannels:
            print "glTexImage2D: GL_ALPHA"
            glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.image.size[0], self.image.size[1], 0, GL_ALPHA, GL_UNSIGNED_BYTE, self.imagestr); #  width == columns
        else:
            print "texture.py: numchannels not handled.", self.numChannels
            raise Exception("Invalid num channels")

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def release(self):
        if (self.glId != 0):
            glDeleteTextures(self.glId)

    def blit(self, destPos, sourceRect, (screenWidth, screenHeight), blend=False, orthoSetup=True, vflipTexture=False):
        # similar to sdl blit
        # Rect has generally: x,y, width, height

        glPushAttrib(GL_ENABLE_BIT) # texture, blend
        if orthoSetup:
            self._orthoSetupPush(screenWidth, screenHeight)
        if blend:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._blitTxtrSetup()
        self._blitOne(destPos, sourceRect, vflipTexture=vflipTexture)
        if orthoSetup:
            self._orthoSetupPop()
        glPopAttrib()

        # Actually, don't bother with draw pixels, since cutting sub-rectangles
        #   has no chance of hardware acceleration and doesn't handle blending.
        #glRasterPos2f(destPos[0], destPos[1])
        #xsize = min(sourceRect.width, self.texture.image.size[0] - sourceRect.x)
        #ysize = min(sourceRect.height,self.texture.image.size[1] - sourceRect.y)
        #glDrawPixels(xsize, ysize, GL_RGBA, GL_UNSIGNED_BYTE,
        #     self.texture.imagestr)

    def blitWithTexScale(self, destPos, sourceRect, (screenWidth, screenHeight), scale, blend=False, orthoSetup=True, vflipTexture=False):
        glPushAttrib(GL_ENABLE_BIT) # texture, blend
        if orthoSetup:
            self._orthoSetupPush(screenWidth, screenHeight)
        if blend:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._blitTxtrSetup()
        self._blitOneWithTexScale(destPos, sourceRect, scale, vflipTexture=vflipTexture)
        if orthoSetup:
            self._orthoSetupPop()
        glPopAttrib()

    def _orthoSetupPush(self, screenWidth, screenHeight):
        # set frustum and set
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, screenWidth, 0, screenHeight)
        glMatrixMode(GL_MODELVIEW)

    def _orthoSetupPop(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _blitTxtrSetup(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

        self.bind()
        #glTexParameteri( GL_TEXTURE_RECTANGLE_NV, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
        #glTexParameteri( GL_TEXTURE_RECTANGLE_NV, GL_TEXTURE_MAG_FILTER, GL_LINEAR );

    def _blitOne(self, destPos, sourceRect, vflipTexture=False):
        DrawTxtrd2dSquareIn2DFromCorner(destPos, sourceRect.width, sourceRect.height, texXMinMax=(float(sourceRect.x) / self.getWidth(), float(sourceRect.x+sourceRect.width) / self.getWidth()), texYMinMax=(float(sourceRect.y) / self.getHeight(), float(sourceRect.y+sourceRect.height) / self.getHeight()), vflipTexture=vflipTexture)
    
    def _blitOneWithTexScale(self, destPos, sourceRect, scale, vflipTexture=False):
        #color=(0,255,0,255)
        #glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, color)
        #pixelAdjust=(50, 0)
        #pixelSize=sourceRect.width / 
        DrawTxtrd2dSquareIn2DFromCorner(destPos, sourceRect.width, sourceRect.height, texXMinMax=(float(sourceRect.x) / (self.getWidth()) / scale[0], float(sourceRect.x+sourceRect.width) / (self.getWidth()) / scale[0]), texYMinMax=(float(sourceRect.y) / self.getHeight() / scale[1], float(sourceRect.y+sourceRect.height) / self.getHeight() / scale[1] ), vflipTexture=vflipTexture)

    def isPixelTransparent( self, imagecoords ):
        pixelColors = self.image.getpixel( (imagecoords[0], self.image.size[1] - imagecoords[1]) )
        if hasattr(pixelColors,'__iter__'): # if list type
            if len(pixelColors) == 4: 
                if pixelColors[3] == 0:
                    return True
            elif len(pixelColors) == 2: 
                if pixelColors[1] == 0:
                    return True
        return False
        
class EasyTexture:
    # Advanced texture functions
    def __init__(self, filename, blend=False, screenGeomRect=None, dstRectScale=None):
        self.texture = Texture(filename)
        if blend:
            self.blendFunc = (GL_SRC_ALPHA, GL_ONE)
        else:
            self.blendFunc = (None, None)
        #(GL_SRC_ALPHA, GL_ONE);
        #(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.txtrMode = M_REPLACE
        # self.txtrTarget = GL_TEXTURE_2D
        # self.alphaTest = False  # assume this for now
        self.nativeWidth, self.nativeHeight = self.texture.getWidth(), self.texture.getHeight()
        self.width, self.height = self.texture.getWidth(), self.texture.getHeight()
        if screenGeomRect == None:
            self.screenGeomRect = Rect(0,0,self.width,self.height)
        else:
            self.screenGeomRect = screenGeomRect

        self.texXMinMax = Vec2(0, 1)
        self.texYMinMax = Vec2(0, 1)
        self.color = None

        if dstRectScale == None:
            self.setDstRectScale( (1.0, 1.0) )
        else:
            self.setDstRectScale(dstRectScale)

    def reloadGLTextureFromData(self):
        self.texture.reloadGLTextureFromData()
        self.nativeWidth, self.nativeHeight = self.texture.getWidth(), self.texture.getHeight()
        if self.dstRectScale == None:
            self.setWidth(self.texture.getWidth())
            self.setHeight(self.texture.getHeight())
        else:
            self.setDstRectScale(self.dstRectScale) # apply scale based on new resolution

    def bind(self):
        self.texture.bind()

    def setTexXMinMax(self, xmin, xmax):
        self.texXMinMax.x = xmin
        self.texXMinMax.y = xmax

    def setTexYMinMax(self, ymin, ymax):
        self.texYMinMax.x = ymin
        self.texYMinMax.y = ymax

    def unbind(self):
        self.texture.unbind()

    def release(self):
        self.texture.release()     

    def draw(self, vflipTexture=False):
        glPushAttrib(GL_ENABLE_BIT)
        glDepthMask(GL_FALSE);    # avoids annoying boxes visible around see through particles
        glEnable(GL_CULL_FACE);

        #if self.alphaTest != None:
        #    #glEnable(GL_ALPHA_TEST);
        #    #glAlphaFunc(GL_GREATER, .5);

        if self.blendFunc == (None,None) :
            glDisable(GL_BLEND)
        else:
            glEnable(GL_BLEND);
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE);
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBlendFunc(self.blendFunc[0], self.blendFunc[1])

        if self.texture != None: # don't have gl textures
            glEnable(GL_TEXTURE_2D)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GLTextureModes[self.txtrMode]);
            #    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, self.txtrMode ); # was GL_DECAL, or GL_MODULATE

        self.texture.bind()
        if (self.color != None):
            glColor4f(self.color[0],
                      self.color[1],
                      self.color[2],
                      self.color[3]);
        unit_up_vec = Vec2(0.0, 1.0)
        edge_vec = Vec2(1.0, 0.0)
        if self.texture != None: # have gl textures
            # print "easy texture draw:", self.screenGeomRect.x, self.screenGeomRect.y , self.screenGeomRect.width,self.screenGeomRect.height, self.texXMinMax, self.texYMinMax
            DrawTxtrd2dSquareIn2DFromCorner(Vec2(self.screenGeomRect.x, self.screenGeomRect.y), self.screenGeomRect.width,self.screenGeomRect.height, self.texXMinMax, self.texYMinMax, vflipTexture=vflipTexture)
        else:
            Draw2dSquareIn2D(Vec2(0,0), self.width, self.height)

        """
        glBegin(GL_TRIANGLE_STRIP)
        glTexCoord2d(0.0, 1.0);
        glVertex2f(200, 400)
        glTexCoord2d(0.0, 0.0);
        glVertex2f(200, 200)
        glTexCoord2d(1.0, 1.0);
        glVertex2f(400, 400)
        glTexCoord2d(1.0, 0.0);
        glVertex2f(400, 200)
        glEnd()
        """
        self.texture.unbind()

        glPopAttrib()

    def setOffsetX(self, x):
        self.screenGeomRect.setX(x)

    def setOffsetY(self, y):
        self.screenGeomRect.setY(y)

    def setPos(self, x, y):
        self.screenGeomRect.setOffset(x,y)

    def getPos(self):
        return self.screenGeomRect.x, self.screenGeomRect.y

    def setDstRectScale(self, dstRectScale):
        self.dstRectScale = dstRectScale
        if self.dstRectScale == None:
            self.setWidth(self.getNativeWidth())
            self.setHeight(self.getNativeHeight())
        else:
            self.setWidth(self.getNativeWidth() * dstRectScale[0])
            self.setHeight(self.getNativeHeight() * dstRectScale[1])

    def setWidth(self, w):
        self.width = w
        self.screenGeomRect.setWidth(w)

    def setHeight(self, h):
        self.height = h
        self.screenGeomRect.setHeight(h)

    def getWidth(self):
        return self.width
    get_width = getWidth

    def getNativeWidth(self):
        return self.nativeWidth

    def getHeight(self):
        return self.height
    get_height = getHeight

    def getNativeHeight(self):
        return self.nativeHeight

    def getRect(self):
        return Rect(0,0,self.width, self.height)

    def zoom(self, factorx, factory):
        # just change max of x and y
        width = self.texXMinMax[1] - self.texXMinMax[0]
        height = self.texYMinMax[1] - self.texYMinMax[0]
        # slightly confusing, the first .y, means "max"
        #             max = min + width / factor
        self.texXMinMax.y = self.texXMinMax[0] + width / factorx
        self.texYMinMax.y = self.texYMinMax[0] + height / factory

    def setZoom(self, factorx, factory):
        # just change max of x and y
        # slightly confusing, the first .y, means "max"
        #             max = min + width / factor
        self.texXMinMax.y = self.texXMinMax[0] + self.nativeWidth / factorx
        self.texYMinMax.y = self.texYMinMax[0] + self.nativeHeight / factory

    def setOffset(self, x, y):
        self.texXMinMax.x = x
        self.texYMinMax.x = y
    setPan = setOffset

    def pan(self, amountx, amounty):
        #self.texXMinMax.x = (self.texXMinMax.x + amountx + 1) % 1.0
        #self.texYMinMax.x = (self.texXMinMax.x + amounty + 1) % 1.0
        #self.texXMinMax.y = (self.texXMinMax.y + amountx + 1) % 1.0
        #self.texYMinMax.y = (self.texXMinMax.y + amounty + 1) % 1.0
        self.texXMinMax.x += amountx
        self.texYMinMax.x += amounty
        self.texXMinMax.y += amountx
        self.texYMinMax.y += amounty

class BoxTxtr2D:
    def __init__(self, txtrFilename):
        self.hasDrawFunc=True
        self.hasEraseDrawFunc=True
        self.visible = True
        self.texture = Texture( "../../commondata/greenfadedsquare.png")
        self.useDrawPixel = False

        def frameUpdate(self, app, secs):
            pass

        def eraseDraw(self, app):
            pass
        def draw(self, app):
            glClearColor(.8, .8, .8, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

            glPushAttrib(GL_ENABLE_BIT)


            # glEnable(GL_BLEND)
            # glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE);

            if not self.useDrawPixel:
                glEnable(GL_TEXTURE_2D)
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
                self.texture.bind()
                # self.texture.rawTex()

                self.texture.bind()
                glBegin(GL_TRIANGLE_STRIP)
                glTexCoord2d(0.0, 1.0);
                glVertex2f(200, 400)
                glTexCoord2d(0.0, 0.0);
                glVertex2f(200, 200)
                glTexCoord2d(1.0, 1.0);
                glVertex2f(400, 400)
                glTexCoord2d(1.0, 0.0);
                glVertex2f(400, 200)
                glEnd()
                self.texture.unbind()

                self.texture.unbind()
                glDisable(GL_TEXTURE_2D)

            else:
                # Drawpixels version
                glRasterPos2f(450, 250)
                glDrawPixels(self.texture.image.size[0], self.texture.image.size[1], GL_RGBA, GL_UNSIGNED_BYTE, self.texture.imagestr)


class DynamicTexture(Texture):
    def __init__(self, width, height, numChannels):
        #self.imagestr = [0 for x in xrange(length)]
        self.imagestr = [random.randrange(0,255) for x in xrange(length)]

