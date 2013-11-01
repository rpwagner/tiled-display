from flapp.texture import Texture, EasyTexture
from flapp.pmath.vec2 import Vec2
from flapp.pmath.rect import Rect
from OpenGL.GL import GL_MAX_TEXTURE_SIZE, glGetInteger
from baseTileDisplayObject import BaseTileDisplayObject 
import traceback

def GetMaxTextureSize():
    maxTxtrSize = glGetInteger(GL_MAX_TEXTURE_SIZE);
    # print "MAX_TEXTURE_SIZE:", maxTxtrSize
    if maxTxtrSize == 0:
        maxTxtrSize = 4096
    return maxTxtrSize

class glBox:
    def __init__(self):
        self.hasDrawFunc=True
        self.hasEraseDrawFunc=True
        self.visible = True

    def update(self, secs, app):
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

class glTxtrBox(BaseTileDisplayObject):
    # The bounds of this object are based on:
    #    pos, imageSize, and scale
    # Use getPos() and getSize() to get bounding rect
    def __init__(self, imageFilename, screenRect, fullRect, absRect, zoom=(4,4), imagePos=None, imageSize=None, blend=False, cropRect=None, scale=None):
        pos = imagePos # FIXME, replace imagePos arg above and its mention in other files with "pos"

        BaseTileDisplayObject.__init__(self, screenRect=screenRect, fullRect=fullRect, absRect=absRect, zoom=zoom, pos=pos, size=imageSize, blend=blend, cropRect=cropRect)

        self.hasDrawFunc=True
        self.hasEraseDrawFunc=True
        self.visible = True
        self.texture = Texture( imageFilename, cropRect=cropRect)
        #self.easyTexture = EasyTexture(imageFilename, screenGeomRect=screenRect, blend=False)
        #self.easyTexture.width = renderer.width * 0.8
        #self.easyTexture.height = renderer.height * 0.8
        #self.easyTexture.width = renderer.width
        #self.easyTexture.height = renderer.height
        self.useDrawPixel = False # For comparison debugging
        self.xvel = 0.1
        self.yvel = 0.1
        self.vflipTexture = False

        # Now in base class
        #self.blend=blend
        #self.zoom = zoom

        #self.easyTexture.zoom(zoom[0], zoom[1])
        #self.easyTexture.setOffset(initialOffset[0], initialOffset[1])
        self.autoPan = False

        if pos:
            self.pos = Vec2(pos[0], pos[1])
        else:
            self.pos = Vec2(0.0, 0.0)

        self.srcImageSize = self.texture.getWidth(), self.texture.getHeight()

        if imageSize == None:
            self.imageSize = self.texture.getWidth(), self.texture.getHeight()
        else:
            self.imageSize = imageSize

        self.scale = scale
        if self.scale != None:
            self.imageSize = self.imageSize[0] * self.scale[0], self.imageSize[1] * self.scale[1]

        self.fullRect = fullRect
        self.absRect = absRect
        self.screenRect = screenRect

    def getScale(self):
        return self.scale

    def setScale(self, (x,y)):
        self.scale = (x,y)
        self.imageSize = self.texture.getWidth() * self.scale[0], self.texture.getHeight() * self.scale[1]

    def reloadSizeFromSource(self):
        self.srcImageSize = self.texture.getWidth(), self.texture.getHeight()

        self.imageSize = self.texture.getWidth(), self.texture.getHeight()

        if self.scale != None:
            self.imageSize = self.imageSize[0] * self.scale[0], self.imageSize[1] * self.scale[1]

    def isPixelTransparent( self, imagecoords ):
        if self.scale != None:
            imagecoords = int(round(imagecoords[0] / self.scale[0])), int(round(imagecoords[1] / self.scale[1]))
        if self.blend and self.texture.isPixelTransparent( imagecoords ):
            return True
        return False

    def getSize(self):
        return self.imageSize

    def getRenderSize(self):
        return self.imageSize

    def getSrcSize(self):
        return self.srcImageSize

    def getWidth(self):
        return self.imageSize[0]

    def getHeight(self):
        return self.imageSize[1]

    def getPos(self):
        return Vec2(self.pos.x, self.pos.y)

    def setPos(self, x, y):
        self.pos = Vec2(x,y)

    def getRect(self):
        return Rect(self.pos.x, self.pos.y, self.imageSize[0], self.imageSize[1])

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

        """
        # convert to local coords
        localBtmLeft = Vec2(self.pos.x - self.absRect.x, self.pos.y - self.absRect.y)
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
        offset = Vec2(globalBtmLeft.x - self.pos.x , globalBtmLeft.y - self.pos.y)
        #size = (globalTopRight.x - globalBtmLeft.x, globalTopRight.y - globalBtmLeft.y + 80)
        size = (globalTopRight.x - globalBtmLeft.x, localTopRight.y - localBtmLeft.y)
        if size[0] > 0 and size[1] > 0:
            #if mpi.rank == 3:
            #    print "renderer height:", renderer.height
            self.texture.blit( localBtmLeft, Rect(offset.x,offset.y, size[0], size[1]), (renderer.width, renderer.height) , blend=self.blend)
        """
        localRect, txtrRect = self.getLocalRectTxtrRectBL()
        # print "pos:", self.pos, "absRect:", self.absRect
        # print "txtrBox LOCAL RECT:", localRect, "TXTR RECT:", txtrRect
        #print dir(localRect)
        localBtmLeft = Vec2(localRect.x, localRect.y)  # probably top and btm are flipped
        localTopRight = Vec2(localRect.x, localRect.y)
        if localRect.width > 0 and localRect.height > 0:
            #self.texture.blit( localBtmLeft, Rect(offset.x,offset.y, size[0], size[1]), (renderer.width, renderer.height) , blend=self.blend)
            #print "Setting image pos to: ", localBtmLeft
            # print "txtrBox Blit:", localBtmLeft, txtrRect, (renderer.width, renderer.height) , self.blend
            if self.scale != None:
                self.texture.blitWithTexScale( localBtmLeft, txtrRect, (renderer.width, renderer.height), self.scale, blend=self.blend, vflipTexture=self.vflipTexture)
            else:
                self.texture.blit( localBtmLeft, txtrRect, (renderer.width, renderer.height) , blend=self.blend, vflipTexture=self.vflipTexture)

        #self.easyTexture.draw()

try:
    #from streamView import StreamView, StartStreamViewLoop, StreamState
    from streamViewCeleritas import StreamView

    class glStreamedTxtrBox(glTxtrBox, StreamView):
        def __init__(self, imageFilename, screenRect, fullRect, absRect, zoom=(4,4), imagePos=None, imageSize=None, blend=False, cropRect=None, scale=None, streamState=None, streamWidth=None, streamHeight=None, vflip=False ):
            pos = imagePos # FIXME, replace imagePos arg above and its mention in other files with "pos"
            glTxtrBox.__init__(self, imageFilename="", screenRect=screenRect, fullRect=fullRect, absRect=absRect, zoom=zoom, imagePos=pos, imageSize=imageSize, blend=blend, cropRect=None, scale=scale)
            self.texture.setSize((2,2)) # just to make visible for debugging

            self.streamWidth = streamWidth
            self.streamHeight = streamHeight
            self.streamState = streamState
            #self.vflipTexture = True # True for flx streaming
            self.vflipTexture = vflip # True for flx streaming
            #print "VFLIP?:", self.vflipTexture

        def update(self, secs, app):
            if self.streamState == None:
                return

            if self.streamState.currentFrame == None:
                # this is only relevant before we have seen any frames.
                pass #self.texture.reloadGLTextureFromData()
            else: # currentFrame != None, we have a video buffer
                try:
                    self.streamState.mainLock.acquire()
                    # print "Setting currentFrame"
                    self.texture.imagestr = self.streamState.currentFrame
                    if type(self.streamWidth) != type(5): # check for number/integer type
                        raise Exception("streamWidth is not a number %s %s" %s (type(streamWidth), streamWidth))
                    #self.texture.size = (352, 288)
                    self.texture.size = (self.streamWidth, self.streamHeight)
                    self.texture.numChannels = 3
                    self.reloadSizeFromSource()
                except:
                    traceback.print_exc()
                finally:
                    self.streamState.mainLock.release()
                self.texture.reloadGLTextureFromData()

        def setStreamState(self, s):
            self.streamState = s

        def draw(self, renderer):
            glTxtrBox.draw(self, renderer)

        def reloadSizeFromSource(self):
            glTxtrBox.reloadSizeFromSource(self)
            if self.scale != None:
                self.setSize( (self.imageSize[0] * self.scale[0], self.imageSize[1] * self.scale[1]) )

        def isPixelTransparent( self, imagecoords ):
            return False

except Exception, e:
    print e, "Fix dependency to support streaming."
    glStreamedTxtrBox = None


