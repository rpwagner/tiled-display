import os
import Image
import traceback
from flapp.movie.utils import GetMovieFPS, GetMovieDuration
import mmap
import resource

class ImageMovieReader:
    ST_STOP = 0
    ST_PLAY = 1
    ST_PAUSE = 2
    def __init__(self, quiet = False):
        self.path = ""
        self.fileLoaded = False
        self.playingFrame = None
        self.state = self.ST_STOP
        self.currentFrameIndex = 0
        # self.duration = 0.0
        self.defaultFps = 24.0
        self.allowFrameSkip=False  # whether frames should be skipped to stay in time
        self.fps = self.defaultFps
        self.discoverFps=True  # whether fps should be discovered automatically.
                               # optional since currently done externally.
        self.movieTime = 0.0
        self.supportedFormats = [".png", ".jpg"]
        self.quiet = quiet

    def setPath(self, path):
        self.path = path

    setFile = setPath

    def getSize(self):
        return (self.width, self.height)

    def preloadFrames(self):
        # Allow more open files than the default
        #resource.setrlimit(resource.RLIMIT_NOFILE, (-1,-1)) # -1 means the max possible

        #print "FILE LIMIT:", resource.getrlimit(resource.RLIMIT_NOFILE)
        softLimit, hardLimit = resource.getrlimit(resource.RLIMIT_NOFILE)
        limit = min(softLimit, hardLimit) - 20
        self.files = self.files[:limit-20]

        self.preloadedFrames = []
        print "preloading ", len(self.files), "files."
        for i in range(len(self.files)):
            path = os.path.join(self.path, self.files[i])
            #self.preloadedFrames.append(open(path).read())
            f = open(path, "r+b")
            memFile = mmap.mmap(f.fileno(), 0)
            memFile.seek(0)
            # memFile.close()
            self.preloadedFrames.append( memFile )
            f.close()

    def readOneFrame(self, index):
        if self.usePreload:
            print "INDEX:", index
            img = Image.open(self.preloadedFrames[index])
            return img
        else:
            path = os.path.join(self.path, self.files[index % len(self.files)])
            img = Image.open(path)
            return img

    getFrameByIndex=readOneFrame

    def getNextFrame(self):
        return self.readOneFrame(self.currentFrameIndex) 

    def loadFile(self, path=None, preload=False):
        if path:
            self.path = path
        if not os.path.exists(self.path):
            raise Exception("Path does not exist: %s" % self.path )
        allFiles = os.listdir(self.path)
        self.files = []
        for f in allFiles:
            if os.path.splitext(f.lower())[1] in self.supportedFormats:
                self.files.append(f)
        self.files.sort()
        print "Number of frames in movie:", len(self.files)

        self.usePreload=preload
        if self.usePreload:
            self.preloadFrames()

        self.frame = self.readOneFrame(0)

        if self.frame.mode == "P":
            self.frame = self.frame.convert("RGBA") 

        # print dir(self.stream.GetFrameNo(0))
        self.width, self.height = self.frame.size

        self.fileLoaded = True
        self.movieTime = 0.0
        self.currentFrameIndex = 0  # frame 0 gotten a few lines above

        # try to read duration and FPS.  Should eventually be done internally 
        #  with additions to pyffmpeg.
        self.fps = self.defaultFps
        if self.discoverFps:
            try:
                self.fps = GetMovieFPS(self.filename)
            except:
                print "Warning: unable to determine movie FPS, using default."
                traceback.print_exc()
        #try:
        #    self.duration = GetMovieDuration(self.filename)
        #except:
        #    print "Warning: unable to determine movie duration (not necessary)"

    def has_alpha(self):
        return False  # for now, maybe later check surface or movie if we play a transparent movie.

    def play(self):
        self.state = self.ST_PLAY

    start = play

    def getNumImageChannels(self):
        return 4;

    def rewindMovie(self):
        self.movieTime = 0.0
        self.currentFrameIndex = 0
        if not self.quiet:
            print "Movie loop restarted"

    def getNumFrames(self):
        return len(self.files)

    def getFrame(self):
        try:
            #img = self.stream.GetFrameTime(self.movieTime)
            # given movieTime and fps
            targetFrame = int(self.fps * self.movieTime)
            #print "Current frame, target frame, movieTime:", self.currentFrameIndex, targetFrame, self.movieTime
            if targetFrame > self.currentFrameIndex:
                if (False == self.allowFrameSkip) or targetFrame-self.currentFrameIndex < 4 :
                    # it can take two frames worth of time to seek, so only do
                    #   it if playback is more than a frame or two too slow.
                    #print "next frame"
                    img = self.getNextFrame()
                    self.currentFrameIndex += 1
                    # import time
                    # time.sleep(0.5) # for debugging
                else:
                    #print "seek frame:", self.currentFrameIndex, targetFrame,"seek offset:", targetFrame - self.currentFrameIndex
                    self.currentFrameIndex = targetFrame
                    img = self.getFrameByIndex(self.currentFrameIndex)
                    # print "Got frame no:", self.currentFrameIndex, targetFrame, img 
            else:
                #print "keep frame", self.currentFrameIndex, targetFrame
                img = None
        except IOError:
            self.rewindMovie()

        if self.currentFrameIndex >= len(self.files):
            self.rewindMovie()

        # print "exiting getFrame, movieTime:", self.movieTime 

        if img != None:
            # img = img.transpose(Image.FLIP_TOP_BOTTOM)
            return img.tostring()
        else:
            return None
        #return img

        """
        if frameNumber != self.playingFrame: # new frame so change the displayed image

            self.rawFrameData = pygame.image.tostring(self.moviePygameSurface,'RGB',1)
            
            self.rawFrameData = [x for x in self.rawFrameData]
            self.rawFrameData = "".join(self.rawFrameData)

            #print "raw data len:", len(self.rawFrameData)
            #print "Raw data:", [ord(x) for x in self.rawFrameData]
        #imagestr = [chr(int(x/3./1022./762.*255 / (x%3+1))) for x in xrange(1022*762*3)]
        #imagestr = "".join(imagestr)
        #return imagestr
        return self.rawFrameData
        """

    def update(self, secs, app):
        if not self.fileLoaded:
            self.loadFile()
            print "LOADED MOVIE FILE"
            return
        if self.fileLoaded and self.state == self.ST_PLAY:
            self.movieTime += secs

    def getMovieTime(self):
        return self.movieTime

    def setMovieTime(self, movieTime):
        self.movieTime = movieTime

    def setAllowFrameSkip(self, boolValue=True):
        self.allowFrameSkip = bool(boolValue)

    def setFps(self, fps):
        self.fps = fps

