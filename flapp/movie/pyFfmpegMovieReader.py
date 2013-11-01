import pyffmpeg
import Image
import traceback
from flapp.movie.utils import GetMovieFPS, GetMovieDuration

DEBUGFRAME=0

class PyFfmpegMovieReader:
    ST_STOP = 0
    ST_PLAY = 1
    ST_PAUSE = 2
    def __init__(self, quiet=False):
        self.filename = ""
        self.fileLoaded = False
        self.playingFrame = None
        self.state = self.ST_STOP
        self.currentFrame = 0
        # self.duration = 0.0
        self.defaultFps = 24.0
        self.allowFrameSkip=False  # whether frames should be skipped to stay in time
        self.fps = self.defaultFps
        self.discoverFps=True  # whether fps should be discovered automatically.
                               # optional since currently done externally.
        self.movieTime = 0.0
        self.quiet = quiet
        self.loopOnFinish = True
        self.finished = False
        self.secsAfterMovieEnd = 0.0
        self.secsAfterMovieEndToRewind = 0.0

    def setSecondsToPauseBeforeRewind(self, value):
        self.secsAfterMovieEndToRewind = value

    def setFile(self, filename):
        self.filename = filename

    def getSize(self):
        return (self.width, self.height)

    def loadFile(self, filename=None):
        if filename:
            self.filename = filename
        #self.movie = pygame.movie.Movie(filename or self.filename)
        self.stream = pyffmpeg.VideoStream()
        self.stream.open(self.filename)
        # stream:
        # GetCurrentFrame(...)
        # GetFrameNo(...)
        # GetFramePts(...)  # Pass in time
        # GetFrameTime(...)
        # GetNextFrame(...)
        # SaveFrame(...)
        # build_index(...)
        # build_index_fast(...)
        # build_index_full(...)
        # dump(...)
        # open(...)

        # print dir(self.stream.GetFrameNo(0))
        self.width, self.height = self.stream.GetFrameNo(0).size

        #print dir(self.movie)
        if filename == None:
            filename = self.filename
        else:
            self.filename = filename

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
        #try:
        #    self.duration = GetMovieDuration(self.filename)
        #except:
        #    print "Warning: unable to determine movie duration (not necessary)"

    def has_alpha(self):
        return False  # for now, maybe later check surface or movie if we play a transparent movie.

    def play(self):
        self.state = self.ST_PLAY

    start = play

    def pause(self):
        self.state = self.ST_PAUSE

    def stop(self):
        self.state = self.ST_STOP

    def togglePause(self):
        if self.ST_PAUSE == self.state or self.ST_STOP == self.state:
            self.play()
        elif self.ST_PLAY == self.state:
            self.pause()

    def getNumImageChannels(self):
        return 4;

    def getFrame(self):
        #print dir(self.stream)
        #frameRate = self.stream.r_frame_rate.num / self.stream.r_frame_rate.den
        #print frameRate
        img = None
        try:
            #img = self.stream.GetFrameTime(self.movieTime)
            # given movieTime and fps
            targetFrame = int(self.fps * self.movieTime)

            if DEBUGFRAME:
                import mpi
                import syncer
                print syncer.GenericSyncer.totalFrameCount, mpi.rank, "Current frame, target frame, movieTime:", self.currentFrame, targetFrame, self.movieTime #, self

            if targetFrame > self.currentFrame:
                """
                diff = targetFrame-self.currentFrame
                if diff > 30: # mainly to avoid long loops if we're at first
                             # frame and we really want the last frame
                    img = self.stream.GetFrameNo(self.currentFrame)
                    self.currentFrame = targetFrame
                    print "SKIP"
                elif diff > 0.5:
                    while targetFrame > self.currentFrame + 0.5:
                        # DEBUG print
                        #print targetFrame, self.currentFrame + 0.5
                        img = self.stream.GetNextFrame()
                        self.currentFrame += 1
                else:
                    pass # stay on current frame and wait
                """
                if (False == self.allowFrameSkip) or targetFrame-self.currentFrame < 4 :
                    # it can take two frames worth of time to seek, so only do
                    #   it if playback is more than a frame or two too slow.
                    #print "next frame"
                    img = self.stream.GetNextFrame()
                    self.currentFrame += 1
                    # import time
                    # time.sleep(0.5) # for debugging
                else:
                    # import mpi
                    # print mpi.rank, "seek frame:", self.currentFrame, targetFrame,"seek offset:", targetFrame - self.currentFrame
                    self.currentFrame = targetFrame
                    img = self.stream.GetFrameNo(self.currentFrame)
                    # print "Got frame no:", self.currentFrame, targetFrame, img 
                
            else:
                if targetFrame == 0 and self.currentFrame != 0: # then rewind
                    if DEBUGFRAME:
                        print syncer.GenericSyncer.totalFrameCount, mpi.rank, "REWIND_B: Current frame, target frame, movieTime:", self.currentFrame, targetFrame, self.movieTime #, self
                    print "INTERNAL REWIND ***********"
                    self.currentFrame = 0
                    img = self.stream.GetFrameNo(self.currentFrame)
                    self.finished = False
                else:
                    #print "keep frame", self.currentFrame, targetFrame
                    img = None
        except IOError:  # Rewind
            if self.loopOnFinish:
                self.finished = True
                if DEBUGFRAME:
                    print syncer.GenericSyncer.totalFrameCount, mpi.rank, "REWIND_A: Current frame, target frame, movieTime:", self.currentFrame, targetFrame, self.movieTime #, self
                if not self.quiet:
                    print "loopOnFinish REWIND ***********"
                """
                self.movieTime = 0.0
                self.currentFrame = 0
                #img = self.stream.GetFrameTime(self.movieTime)
                img = self.stream.GetFrameNo(0)
                if not self.quiet:
                    print "Movie loop restarted"
                """
            else:
                if DEBUGFRAME:
                    print syncer.GenericSyncer.totalFrameCount, mpi.rank, "FINISH_A: Current frame, target frame, movieTime:", self.currentFrame, targetFrame, self.movieTime #, self
                self.finished = True

        # print "exiting getFrame, movieTime:", self.movieTime 
        if DEBUGFRAME:
            print syncer.GenericSyncer.totalFrameCount, mpi.rank, "END: Current frame, target frame, movieTime:", self.currentFrame, targetFrame, self.movieTime #, self

        if img != None:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            return img.tostring()
        else:
            return None
        #return img

        #return self.movie.get_frame()
        #print dir(self.moviePygameSurface)
        print "got frame", self.movie.get_frame()
        frameNumber = self.movie.get_frame()
        if frameNumber != self.playingFrame: # new frame so change the displayed image
            #print "alpha?", self.moviePygameSurface.get_alpha()

            #width, height = self.movie.get_size()
            #print "movie size:", width, height

            self.rawFrameData = pygame.image.tostring(self.moviePygameSurface,'RGB',1)
            
            #for i in range(len(self.rawFrameData)):
            self.rawFrameData = [x for x in self.rawFrameData]
            #    self.rawFrameData[i] = "z"
            self.rawFrameData = "".join(self.rawFrameData)

            #print "raw data len:", len(self.rawFrameData)
            #print "Raw data:", [ord(x) for x in self.rawFrameData]
            self.playingFrame = frameNumber
        #imagestr = [chr(int(x/3./1022./762.*255 / (x%3+1))) for x in xrange(1022*762*3)]
        #imagestr = "".join(imagestr)
        #return imagestr
        return self.rawFrameData

    def rewind(self):
        # print "func REWIND ***********"
        self.movieTime = 0.0
        self.currentFrame = 0 
        self.secsAfterMovieEnd = 0.0
        #img = self.stream.GetFrameTime(self.movieTime)
        img = self.stream.GetFrameNo(0)
        #self.getFrame() # try to avoid blank/checkboard first screen
        if not self.quiet:
            print "Movie loop restarted"
        self.finished = False

    def hasFinished(self):
        return self.finished

    def update(self, secs, app):
        if self.fps > 0.0:
            secs = min(secs, 1.0 / self.fps)
        if DEBUGFRAME:
            import mpi
            import syncer
            print syncer.GenericSyncer.totalFrameCount, mpi.rank, "UPDATE_A: Current frame, movieTime:", self.currentFrame, self.movieTime, self.finished #, self
        if not self.fileLoaded:
            self.loadFile()
            print "LOADED MOVIE FILE"
            return
        if self.fileLoaded and self.state == self.ST_PLAY:
            self.movieTime += secs

            # Check if it's time to rewind
            if self.loopOnFinish:
                if self.finished:
                    self.secsAfterMovieEnd += secs
                    if self.secsAfterMovieEnd > self.secsAfterMovieEndToRewind:
                        self.rewind();

    def getMovieTime(self):
        return self.movieTime

    def setMovieTime(self, movieTime):
        self.movieTime = movieTime

    def skipForward(self, secs):
        self.setMovieTime(self.getMovieTime() + secs)

    def skipBack(self, secs):
        self.setMovieTime( min(self.getMovieTime() - secs, 0) )

    def setAllowFrameSkip(self, boolValue=True):
        self.allowFrameSkip = bool(boolValue)

    def setFps(self, fps):
        self.fps = fps

    def setLoopOnFinish(self, boolValue):
        self.loopOnFinish = boolValue

