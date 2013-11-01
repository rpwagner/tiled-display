import os
from flapp.texture import Texture, EasyTexture

class GLMoviePlayer:
    def __init__(self, origWidth=800, origHeight=600, textureScale=None, dstRectScale=None):
        self.hasDrawFunc=True
        self.hasEraseDrawFunc=False
        self.visible = True
        #self.texture = Texture( "../data/test1.png")
        tmpImageFile = "../data/test1_darkgray.png"
        if not os.path.exists(tmpImageFile):
            tmpImageFile = "data/test1_darkgray.png"
        self.easyTexture = EasyTexture(tmpImageFile)
        self.easyTexture.setWidth(origWidth)
        self.easyTexture.setHeight(origHeight)
        self.videoSrc=None

        self.setTextureScale(textureScale)
        self.setDstRectScale(dstRectScale)

    def setDstRectScale(self, dstRectScale):
        self.dstRectScale = dstRectScale
        self.easyTexture.setDstRectScale(dstRectScale)

    def setTextureScale(self, textureScale):
        self.textureScale = textureScale
        if textureScale == None:
            self.easyTexture.setTexXMinMax(0.0,  1.0)
            self.easyTexture.setTexYMinMax(0.0,  1.0)
        else:
            self.easyTexture.setTexXMinMax(0,  1.0 / textureScale[0] )
            self.easyTexture.setTexYMinMax(0,  1.0 / textureScale[1] )

    def setVideoSource(self, src):
        self.videoSrc=src

    def getVideoSource(self):
        return self.videoSrc

    def update(self, secs, app, visible=True):
        if self.videoSrc == None:
            length = self.easyTexture.texture.image.size[0] * self.easyTexture.texture.image.size[1] * self.easyTexture.texture.numChannels
            self.easyTexture.texture.imagestr = [random.randrange(0,255) for x in xrange(length)]
            self.easyTexture.reloadGLTextureFromData()
        else:
            # print "**** UPDATING", self
            self.videoSrc.update(secs, app)
            #self.easyTexture.texture.size = self.videoSrc.getSize()
            #if not self.videoSrc.has_alpha():
            #    self.easyTexture.texture.numChannels = 3
            #else:
            #    self.easyTexture.texture.numChannels = 4
            imagestr = self.videoSrc.getFrame()
            if imagestr != None:
                self.easyTexture.texture.setSize(self.videoSrc.getSize(), numChannels=self.videoSrc.getNumImageChannels())
                self.easyTexture.texture.imagestr = imagestr
                # testt generated image
                #self.easyTexture.texture.imagestr = [chr(int(x/3./1022./762.*255 / (x%3+1))) for x in xrange(1022*762*3)]
                #self.easyTexture.texture.imagestr = "".join(self.easyTexture.texture.imagestr)

                #self.easyTexture.texture.numChannels = self.videoSrc.getNumImageChannels()
                self.easyTexture.reloadGLTextureFromData()

    def setPos(self, posx, posy):
        self.easyTexture.setPos(posx, posy)

    def getPos(self):
        return self.easyTexture.getPos()

    def draw(self, renderer):
        #glClearColor(.8, .8, .8, 1.0)
        #glClear(GL_COLOR_BUFFER_BIT)
        # glPixelStoref(GL_UNPACK_ALIGNMENT, 1)

        # self.texture.blit( Vec2(10,10), Rect(10,10, 30,30), (app.width, app.height) )
        # self.texture.blit( Vec2(50,50), Rect(0,0, 64,64), (app.width, app.height) )
        # self.texture.blit( Vec2(150,50), Rect(40,40, 64,64), (app.width, app.height) , blend=True)
        #self.easyTexture.texture.blit( Vec2(0.1 * renderer.width,0.1 * renderer.height), Rect(0,0, 30,30), (renderer.width, renderer.height) )
        #from flapp.pmath.rect import Rect
        #from flapp.pmath.vec2 import Vec2
        #self.easyTexture.texture.blit( Vec2(10,10), Rect(0,0, 1000,700), (renderer.width, renderer.height) )
        #print "MOVIE PLAYER DRAWING:", self.easyTexture.screenGeomRect
        self.easyTexture.draw()

    def setAllowFrameSkip(self, boolValue):
       if self.videoSrc:
           self.videoSrc.setAllowFrameSkip(boolValue)
