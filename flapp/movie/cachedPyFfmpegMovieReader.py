import pyffmpeg
from flapp.movie.utils import GetMovieFPS, GetMovieDuration
import Image
import traceback

class CachedPyFfmpegMovieReader:
    ST_STOP = 0
    ST_PLAY = 1
    ST_PAUSE = 2

    def __init__(self, quiet=False):
        self.frames = []
        self.movieTime = 0.0
        self.currentFrame = 0  # frame 0 gotten a few lines above
        self.defaultFps = 24.0
        self.fps = self.defaultFps
        self.discoverFps=True  # whether fps should be discovered automatically.
                               # optional since currently done externally.
        self.loopOnFinish = True
        self.finished = False
        self.quiet = quiet
        self.secsAfterMovieEnd = 0.0
        self.secsAfterMovieEndToRewind = 0.0

    def loadFile(self, filename=None):
        if filename:
            self.filename = filename

        self.stream = pyffmpeg.VideoStream()
        self.stream.open(self.filename)

        # print dir(self.stream.GetFrameNo(0))
        self.width, self.height = self.stream.GetFrameNo(0).size

        #print dir(self.movie)

        self.fileLoaded = True
        self.movieTime = 0.0
        self.currentFrame = 0  # frame 0 gotten a few lines above

        # try to read duration and FPS.  Should eventually be done internally 
        #  with additions to pyffmpeg.
        self.fps = self.defaultFps
        if self.discoverFps:
            try:
                self.fps = GetMovieFPS(self.filename)
            except:
                print "Warning: unable to determine movie FPS, using default."
                traceback.print_exc()
        try:
            while 1:
                img = self.stream.GetNextFrame()
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                self.frames.append(img.tostring())
        except IOError:
            pass #end of movie

        if not self.quiet:
            print "cachedPyFfmpegMovieReader finished caching frames"
        #print dir(self.stream)
        #self.stream.close()
        del self.stream
        self.stream = None  # DEBUG

    def clearCache(self):
        self.frames = []

    def setSecondsToPauseBeforeRewind(self, value):
        self.secsAfterMovieEndToRewind = value

    def play(self):
        self.state = self.ST_PLAY

    start = play

    def pause(self):
        self.state = self.ST_PAUSE

    def stop(self):
        self.state = self.ST_STOP

    def getSize(self):
        return (self.width, self.height)

    def getNumImageChannels(self):
        return 4;

    def getFrame(self):
        targetFrame = int(0.5 + (self.fps * self.movieTime)) # + 0.5 is just to round
        targetFrame = targetFrame % len(self.frames)
        return self.frames[targetFrame]

    def rewind(self):
        # print "func REWIND ***********"
        self.movieTime = 0.0
        self.currentFrame = 0 
        self.secsAfterMovieEnd = 0.0
        img = self.stream.GetFrameNo(0)
        if not self.quiet:
            print "Movie loop restarted"
        self.finished = False

    def hasFinished(self):
        return self.finished

    def update(self, secs, app):
        if not self.fileLoaded:
            self.loadFile()
            print "LOADED MOVIE FILE"
            return
        if self.fileLoaded and self.state == self.ST_PLAY:
            #print self.state
            self.movieTime += secs

            # Check if it's time to rewind
            if self.loopOnFinish:
                if self.finished:
                    self.secsAfterMovieEnd += secs
                    if self.secsAfterMovieEnd > self.secsAfterMovieEndToRewind:
                        self.rewind();

    def setFile(self, filename):
        self.filename = filename

    def getMovieTime(self):
        return self.movieTime

    def setMovieTime(self, movieTime):
        self.movieTime = movieTime

    def skipForward(self, secs):
        self.setMovieTime(self.getMovieTime() + secs)

    def skipBackward(self, secs):
        self.setMovieTime( min(self.getMovieTime() - secs, 0) )

    def setAllowFrameSkip(self, boolValue=True):
        self.allowFrameSkip = bool(boolValue)

    def setFps(self, fps):
        self.fps = fps

    def setLoopOnFinish(self, boolValue):
        self.loopOnFinish = boolValue

