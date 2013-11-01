import os
from glUtils import glTxtrBox, GetMaxTextureSize
from baseTileDisplayObject import BaseTileDisplayObject, NullTileDisplayObject
from groupObject import GroupObject
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2
try:
    from flapp.movie.pyFfmpegMovieReader import PyFfmpegMovieReader
except Exception, e:
    print "WARNING, unable to import pyFfmpegMovieReader" 
    PyFfmpegMovieReader = None
from flapp.movie.imageMovieReader import ImageMovieReader
from flapp.movie.glMoviePlayer import GLMoviePlayer
from groupObject import GroupObject
import Image
import math
from flTileMpi import mpi


def IsMovieFile(filename):
    extension = (filename.split(".")[-1]).lower()
    if extension in ["mpg", "mp4", "mov", "vob", "avi", "ogv"]:
        return True

def IsTiledMoviePath(filename):
    extension = (filename.split(".")[-1]).lower()
    if extension in ["tdmovie"]:
        return True

def IsTiledMovieChunkImageBased(path):
    if os.path.isdir(path): 
        possibleImageList = os.listdir(path)  # directory for each tile
        # Sample 10 or so filenames in case there are extra files like the description .txt file.
        for f in possibleImageList[:10]:
            if os.path.splitext(f.lower())[1] in [".png", ".jpg"]:
                return True
    return False

class TiledMovieObject(BaseTileDisplayObject):
    def __init__(self, filename, screenRect, fullRect, absRect, zoom=(4,4), pos=None, size=None, blend=False, cropRect=None, fps=None, scale=None, allowFrameSkip=True):
        BaseTileDisplayObject.__init__(self, screenRect=screenRect, fullRect=fullRect, absRect=absRect, zoom=zoom, pos=pos, size=size, blend=blend, cropRect=cropRect)

        if IsTiledMovieChunkImageBased(filename):
            print "Using ImageMovieReader"
            r = ImageMovieReader(quiet = True)
        else:
            print "Using PyFfmpegMovieReader"
            if not PyFfmpegMovieReader:
                print "PyFfmpegMovieReader is not available, make sure pyffmpeg and pyFfmpegMoviereader are installed before playing a movie."
            r = PyFfmpegMovieReader(quiet=True)
            r.setSecondsToPauseBeforeRewind(1.0)
        if fps != None:
            r.setFps(fps)
            r.discoverFps = False

        self.scale = scale
        self.movieReader = r
        #r.setFile("/home/eolson/blah_mpeg1.mpg")
        self.filename = filename
        r.setFile(self.filename)
        r.loadFile()
        print "Setting movie size:", r.getSize()
        self.moviePlayer = GLMoviePlayer(origWidth=r.getSize()[0], origHeight=r.getSize()[1], textureScale=scale, dstRectScale=scale)
        #                                         note textureScale unused since local code replaces moviePlayer's draw function()
        self.moviePlayer.setAllowFrameSkip(allowFrameSkip) # because we want to 
                          # getNextFrame if it's not on current tile's display (for draggable movies)
        self.size = tuple(r.getSize())
        if self.scale != None:
            self.size = self.size[0] * self.scale[0], self.size[1]* self.scale[1]
        if pos: # avoid None
            self.moviePlayer.setPos(pos[0], pos[1])
            self.moviePlayer.setPos(0,0)
            self.setPos(*pos)
            print "TileMovieOBject.__init__, SETTING pos:", self.getPos()
        else:
            print "Pos is:", pos
            #raise
            print "WARNING DEBUG setting movie pos to 0,0"
            self.moviePlayer.setPos(0,0)
            self.setPos(0,0)
        self.moviePlayer.setVideoSource(r)
        print "TileMovieOBject.__init__, pos:", self.getPos()
        r.start()

    def draw(self, renderer):
        if self.hidden:
            return
        localRectBL, txtrRectBL = self.getLocalRectTxtrRectBL()
        # print "pos:", self.pos, "absRect:", self.absRect
        # print "movie LOCAL RECT:", localRectBL, "TXTR RECTBL:", txtrRectBL
        localBtmLeftBL = Vec2(localRectBL.x, localRectBL.y)  # probably top and btm are flipped
        #localTopRightTL = Vec2(localRect.x, localRect.y)
        #localBtmLeftBL = Vec2(localRectBL.x, self.screenRect.height-localRectBL.y)
        #localBtmRightBL = Vec2(localRectBL.x, localBtmLeftBL.y + localRectBL.height)
        #print "Drawing at:", localBtmLeft
        if abs(localRectBL.width) > 0 and abs(localRectBL.height) > 0:
            #self.texture.blit( localBtmLeft, Rect(offset.x,offset.y, size[0], size[1]), (renderer.width, renderer.height) , blend=self.blend)
            #self.texture.blit( localBtmLeft, localRectBL, (renderer.width, renderer.height) , blend=self.blend)
            # use GL coords (bottom left is 0,0)
            #print "Setting movie pos to: ", localBtmLeftBL
            #self.moviePlayer.setPos(*(txtrBtmLeftBL))
            #self.moviePlayer.setPos(10,-340)
            # self.moviePlayer.setPos(30,10)
            #self.moviePlayer.setPos(*(localBtmLeft - Vec2(txtrRect.x, -txtrRect.y)))
            blend = False
            # print "movieplayer blit:", localBtmLeftBL, txtrRectBL, (renderer.width, renderer.height) , blend

            # Do simple blit for now instead of using easyTexture features.
            if self.scale == None:
                self.moviePlayer.easyTexture.texture.blit( localBtmLeftBL, txtrRectBL, (renderer.width, renderer.height) , blend=blend)
            else:
                self.moviePlayer.easyTexture.texture.blitWithTexScale( localBtmLeftBL, txtrRectBL, (renderer.width, renderer.height) , self.scale, blend=blend)
            """
            self.moviePlayer.setPos(*(localBtmLeftBL))
            self.moviePlayer.easyTexture.setWidth(localRectBL.width)
            self.moviePlayer.easyTexture.setHeight(localRectBL.height)
            self.moviePlayer.easyTexture.setTexXMinMax(txtrRectBL.x, txtrRectBL.x + txtrRectBL.width)
            self.moviePlayer.easyTexture.setTexXMinMax(txtrRectBL.y, txtrRectBL.y + txtrRectBL.height)
            self.moviePlayer.draw(renderer)
            """

    def isOnScreen(self):
        # next lines copied from draw()
        localRectBL, txtrRectBL = self.getLocalRectTxtrRectBL()
        # print "local rect:", localRectBL
        pos = self.getPos()
        if localRectBL.x <= pos.x <= (localRectBL.x + localRectBL.width) and \
           localRectBL.y <= pos.y <= (localRectBL.y + localRectBL.height):
           return True
        else:
           return False
           
    def update(self, secs, app):
        visible = self.isOnScreen()
        # print "visible:", visible
        self.moviePlayer.update(secs, app, visible=visible)
        #self.moviePlayer.update(secs, app)

    def isPixelTransparent(self, (x,y) ):
        return False

    def getRect(self):
        return Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

    def getWidth(self):
        return self.size[0]

    def getHeight(self):
        return self.size[1]

    def setMovieTime(self, movieTime):
        self.movieReader.setMovieTime(movieTime)

    def getMovieTime(self):
        return self.movieReader.getMovieTime()

    def getMovieDuration(self):
        return self.movieReader.getMovieDuration()

    def togglePause(self):
        self.movieReader.togglePause()

    def skipBack(self, secs):
        self.movieReader.skipBack(secs)

    def skipForward(self, secs):
        self.movieReader.skipForward(secs)
        
    def pause(self):
        self.movieReader.pause()

    stop = pause

    def play(self):
        self.movieReader.play()

    start = play

    def hasFinished(self):
        return self.movieReader.hasFinished()

    def rewind(self):
        return self.movieReader.rewind()

    def setLoopOnFinish(self, boolValue):
        return self.movieReader.setLoopOnFinish(boolValue)

    def getSize(self):
        return self.size


def CreateDumbMovieObjectOnEachTile(filename, pos):
    # for debugging
    r = PyFfmpegMovieReader()
    r.setFile("/home/eolson/blah_mpeg1.mpg")
    r.loadFile()
    moviePlayer = GLMoviePlayer(origWidth=r.getSize()[0], origHeight=r.getSize()[1])
    moviePlayer.setVideoSource(r)
    moviePlayer.setPos(pos[0], pos[1])
    r.start()
    return moviePlayer


class TiledMovieGroupObject(GroupObject):
    # Group object with minor tiled movie additions such
    #   as a frame time to sync all movie tiles.
    def __init__(self, name, objectsToGroup=None, duration = None, fps=None):
        GroupObject.__init__(self, name, objectsToGroup)

        if self.getFirstNonNullChild() == None:
            self.keepMovieTimeLocally = True
            if duration == None:
                raise Exception("Tiled Movie duration is unknown, please ensure there is a duration entry in the description.txt")
            if fps == None:
                raise Exception("Tiled Movie FPS is unknown, please ensure there is a FPS entry in the description.txt")
            self.localMovieDuration = duration
            self.localMovieFps = fps
            self.localMovieFrameTime = 1.0 / fps
            self.localMovieTime = 0.0
            #self.localMovieNumFrames = 0
            #self.localCurrentFrame = 0
            print "NOTE: TiledMovieGroupObject:keeping time locally (no movie tile to decode on this node)"
        else:
            self.keepMovieTimeLocally = False
        #self.keepMovieTimeLocally = False  # comment out to make it obvious when keepMovieTimeLocally is being used.

    def update(self, secs, app):
        if  self.keepMovieTimeLocally:
            self.localMovieTime += self.localMovieFrameTime
            #self.localCurrentFrame += 1
            if self.localMovieTime > self.localMovieDuration + self.localMovieFrameTime:
                self.localMovieTime = 0.0
                #self.localCurrentFrame = 0

        # set positions, etc.
        GroupObject.update(self, secs, app)

        # set global movie time after children have updated their internal time.
        #for child, offset in self.childrenAndOffsets.items():
        #    if hasattr(child, "getVideoSrc"):
        #        child.getVideoSrc().setMovieTime(self.movieTime)

    # Next two functions are for synchronizing
    def storeDataInDict(self, d):
        key = "movieTime_%s" % self.name 
        #d[key] = self.movieTime
        d[key] = self.getMovieTime()

    def setDataFromDict(self, d):
        # print "MOVIE TILE RECEIVE DATA:", d
        key = "movieTime_%s" % self.name 
        if key in d:
            self.movieTime = d[key]
            # print "SETTING MOVIE TIME:", d[key], key
            for child in self.childrenAndOffsets.keys():
                if hasattr(child, "setMovieTime"): # don't set for Null objs
                    child.setMovieTime(self.movieTime)

    def getFirstNonNullChild(self):
        for child in self.childrenAndOffsets.keys():
            if not isinstance(child, NullTileDisplayObject):
                return child
        return None

    def getMovieTime(self):
        if  self.keepMovieTimeLocally:
            return self.localMovieTime
        else:
            child = self.getFirstNonNullChild()
            if None != child:
                return child.getMovieTime()
            else:
                print "WARNING: only NULL objects (TiledMovieGroupObject.getMovieTime())"
                return 0.0
        #if len(self.childrenAndOffsets) > 0:
        #    return self.childrenAndOffsets.keys()[0].getMovieTime()
        #else:
        #    return 0.0

    def getDuration(self):
        if  self.keepMovieTimeLocally:
            return self.localMovieDuration
        else:
            if len(self.childrenAndOffsets) > 0:
                return self.childrenAndOffsets.keys()[0].getDuration()
            else:
                print "WARNING: only NULL objects (TiledMovieGroupObject.getDuration())"
                return 0.0
        

    def isPixelTransparent(self, (x,y) ):
        return False

    def hasFinished(self):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                if child.hasFinished():
                    return True

    def togglePause(self):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.togglePause()

    def skipBack(self, secs):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.skipBack(secs)

    def skipForward(self, secs):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.skipForward(secs)

    def pause(self):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.pause()

    stop = pause

    def play(self):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.play()

    start = play

    def rewind(self):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.rewind()

    def setLoopOnFinish(self, boolValue):
        for child in self.getChildren():
            if not isinstance(child, NullTileDisplayObject):
                child.setLoopOnFinish(boolValue)

    """
    def show(self):
        for child in self.getChildren():
            child.show()

    def hide(self):
        for child in self.getChildren():
            child.hide()
    """

