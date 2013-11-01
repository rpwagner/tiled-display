import pygame.movie 
from pygame import Rect

class PygameMovieReader:
    ST_STOP = 0
    ST_PLAY = 1
    ST_PAUSE = 2
    def __init__(self):
        self.filename = ""
        self.fileLoaded = False
        self.playingFrame = None
        self.state = self.ST_STOP

    def setFile(self, filename):
        self.filename = filename

    def getSize(self):
        return self.movie.get_size()

    def getNumImageChannels(self):
        return 3;

    def loadFile(self, filename=None):
        self.movie = pygame.movie.Movie(filename or self.filename)
        width, height = self.movie.get_size()
        #print "CREATING MOVIE SURFACE:", width, height
        self.moviePygameSurface = pygame.surface.Surface((width,height))
        #print "movie surface", self.moviePygameSurface.get_size()
        self.movie.set_display(self.moviePygameSurface, Rect(0,0,width,height))
        self.currentFrame = self.movie.get_frame()
        #print dir(self.movie)
        if filename == None:
            filename = self.filename
        else:
            self.filename = filename

        self.fileLoaded = True

    def has_alpha(self):
        return False  # for now, maybe later check surface or movie if we play a transparent movie.

    def play(self):
        self.state = self.ST_PLAY

    def _play(self):
        self.movie.play()

    start = play

    def getFrame(self):
        #return self.movie.get_frame()
        #print dir(self.moviePygameSurface)
        #print "got frame", self.movie.get_frame()
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

    def update(self, secs, app):
        if not self.fileLoaded:
            self.loadFile()
            print "LOADED MOVIE FILE"
            return
        if self.fileLoaded and self.state == self.ST_PLAY and not self.movie.get_busy():
            # get_busy() is True if movie is playing.
            self._play()

