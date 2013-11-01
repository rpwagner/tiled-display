from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2

class BaseTileDisplayObject:
    def __init__(self, screenRect, fullRect, absRect, zoom=(4,4), pos=None, size=None, blend=False, cropRect=None):
        self.screenRect = screenRect
        self.fullRect = fullRect
        self.absRect = absRect
        if pos:
            self.pos = Vec2(pos[0], pos[1])
        else:
            self.pos = Vec2(0.0, 0.0)
        print "BaseTileDisplayObject, size arg unused"
        """
        if not size:  # if size == None:
            self.size = 100,100
        else:
            self.size = size
        """
        self.blend = blend
        self.cropRect=cropRect
        self.hidden = False

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def isHidden(self):
        return self.hidden

    def getLocalRectTxtrRectBL(self):
        # convert to local coords, BL means 0,0 is in the Bottom Left
        localBtmLeft = Vec2(self.pos.x - self.absRect.x, self.pos.y - self.absRect.y)
        # print "CALC LOCAL TR1:", localBtmLeft.x, self.getSize()[0], localBtmLeft.y, self.getSize()[1]
        localTopRight = Vec2(localBtmLeft.x + self.getSize()[0], localBtmLeft.y + self.getSize()[1])
        # clip to max/min of local display
        localBtmLeft = Vec2(max(localBtmLeft.x, 0), max(localBtmLeft.y, 0))
        #if mpi.rank == 3:
        #    print "clip top right y:", localTopRight.y, self.screenRect.height
        # print "CALC LOCAL TR:", localTopRight.x, self.screenRect.width, localTopRight.y, self.screenRect.height
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

        # print "CALC LOCALRECTSIZE:", localTopRight, localBtmLeft
        localRectSize = localTopRight-localBtmLeft
        return Rect(localBtmLeft.x, localBtmLeft.y, localRectSize[0], localRectSize[1]), Rect(offset.x, offset.y, size[0], size[1])

    def getSize(self):
        raise Exception("ERROR: baseTileDisplayObject.getSize unimplemented.  It needs to be implemented in derived class: %s " % self.__class__)
    """
    def getSize(self):
        return self.size

    def setSize(self, s):
        self.size = (s[0], s[1])
            """

    def getPos(self):
        return self.pos

    def setPos(self,x,y):
        self.pos = Vec2(x,y)

    """ Example Draw function, or look at current glTxtrBox or TiledMovieObject funcs
    def draw(self, renderer):
        localRect, txtrRect = self.getLocalRectTxtrRectBL()
        localBtmLeft = Vec2(localRect.x, localRect.y)  # probably top and btm are flipped
        localTopRight = Vec2(localRect.x, localRect.y)
        #print "Drawing at:", localBtmLeft
        if localRect.width > 0 and localRect.height > 0:
            #self.texture.blit( localBtmLeft, Rect(offset.x,offset.y, size[0], size[1]), (renderer.width, renderer.height) , blend=self.blend)
            #self.texture.blit( localBtmLeft, txtrRect, (renderer.width, renderer.height) , blend=self.blend)
            self.moviePlayer.setPos(*localBtmLeft)
            self.moviePlayer.draw(renderer)
    """

class NullTileDisplayObject(BaseTileDisplayObject):
    def __init__(self, screenRect=None, fullRect=None, absRect=None, zoom=(4,4), pos=None, size=None, blend=False, cropRect=None):
        BaseTileDisplayObject.__init__(self, screenRect, fullRect, absRect, zoom=zoom, pos=pos, size=size, blend=blend, cropRect=cropRect)
        self.size=size
 
    def draw(self, renderer):
        pass

    def isPixelTransparent(self, (x,y) ):
        return True

    def getRect(self):
        if self.pos and self.getSize(): # avoid None
            return Rect(self.pos.x, self.pos.y, self.getSize()[0], self.getSize()[1])
        else:
            return None

    def getWidth(self):
        return self.getSize()[0]

    def getHeight(self):
        return self.getSize()[1]

    def update(self, secs, app):
        pass

    def getSize(self):
        return self.size

