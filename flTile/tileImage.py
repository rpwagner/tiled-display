#!/usr/bin/python
import sys, os, time
import traceback
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path
sys.path = ["/home/eolson/src/vpmedia/pyRTPVideo" ] + sys.path
from random import randrange
import traceback
import pygame
from optparse import Option, OptionParser
import Image
from movieSequence import MovieSequence

# Import mpi from this wrapper module.
# When this app is started with pyMPI, "import mpi"
# will work successfully.  When started with
# plain "python", fakeMpi is used to show that
# there is only one process.
from flTileMpi import mpi

from flapp.app import App
from flapp.glRenderer2D import glRenderer2D
from flapp.pmath.rect import Rect
from flapp.glDrawUtils import ScreenClearer

from socket import gethostname, getfqdn
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

from objectDescription import ObjectDescription, ObjType, ObjectDescription as ObjDesc, StreamObjDescription, GroupedStreamObjDescription, StreamProtocols
from layoutReader import ReadLayout

from visualsManager import VisualsManager
from appState import AppState

#import debugFile

global gWiiSupported
global gStreamingSupported
try:
    from flWii.moteCursor import MoteMouse
    from flWii.moteDetector import MoteDetector
    from flWii.mote import MoteConnectFailed
    from moteManager import MoteManager, SetupMoteControl
    gWiiSupported = True
except Exception, e:
    #traceback.print_exc()
    print "wii mote not enabled, dependencies not found: ", e
    gWiiSupported = False

# ECO testing airstream (not local wii)
gWiiSupported = False

gStreamingSupported = False
gFlxStreamingSupported = False
gCeleritasStreamingSupported = False
try:
    import streamView
    gStreamingSupported = True
    gFlxStreamingSupported = True
except:
    #traceback.print_exc()
    print "FLX Streaming not enabled, streamView import failed."

try:
    import streamViewCeleritas
    gStreamingSupported = True
    gCeleritasStreamingSupported = True
except:
    #traceback.print_exc()
    print "Celeritas Streaming not enabled, streamViewCeleritas import failed."

global gPositionsIndex
gPositionsIndex = 0;

from syncer import GenericSyncer, Syncer
from configUI import ConfigUI
from tileMote import TileMote
from glUtils import glBox, glTxtrBox
from tileMote import TileMote
from tileDisplayObject import CreateTileDisplayObject, GetTiledMoviePathDims, IsImagePath, CreateTileDisplayStreamObject, CreateGroupTileDisplayStreamObject, CreateMultiNetGroupTileDisplayStreamObject, CreateTiledMovieObjectFromLayout
from movieTileDisplayObject import TiledMovieGroupObject, IsTiledMoviePath
from groupTiledStreamObject import GroupTiledStreamObject

global gProfile
global gProfileCount
gProfile = None
gProfileCount = 0

def setupLocalConfig(tConfig, options):
    # fqdn = getfqdn()
    hostname = gethostname()
    forcedHostnameList = None
    if options.hostnames and len(options.hostnames) > 0:
        forcedHostnameList = options.hostnames.split(",")
        #debugFile.write("cmdline hostnames: %s\n" % forcedHostnameList)
        #debugFile.flush()
    elif "TD_HOSTNAMES" in os.environ:   # allow overriding of hostnames per proc
        forcedHostnameList = os.environ[TD_HOSTNAMES].split(",")
        #debugFile.write("TD_HOSTNAMES: %s\n"% os.environ["TD_HOSTNAMES"])
        #debugFile.flush()
    else:
        pass#debugFile.write("NO TD_HOSTNAMES\n")
        #debugFile.flush()
    if forcedHostnameList and len(forcedHostnameList) > 0:
        if len(forcedHostnameList) > mpi.rank:
            hostname=forcedHostnameList[mpi.rank].strip()
    print "hostname:", hostname
    global machineDesc
    #debugFile.write("local config hostname: %s\n"% hostname)
    #debugFile.flush()

    machineDescs = tConfig.getMachineDescsByHostname(hostname)
    if 0 == len(machineDescs):
        raise Exception( "No machine description found for hostname: %s" % hostname)

    descsPerMachine = len(machineDescs)
    if descsPerMachine > 1:
        machineIndex = int(float(mpi.rank) / mpi.procs * descsPerMachine)
        print "host,rank,descIndex,numDescs", hostname, mpi.rank, machineIndex, len(machineDescs)
    else:
        machineIndex = 0

    machineDesc = machineDescs[machineIndex]
 
    global localRects
    localRects = []
    global absoluteRects
    absoluteRects = []
    global localWindows
    for tile in machineDesc.tiles:
        localRects.append(tConfig.getLocalDrawRect(tile.uid))
        absoluteRects.append(tConfig.getAbsoluteFullDisplayRect(tile.uid))
        windowId=tConfig.getLocalWindowFromTileId(tile.uid)
        #if windowId not in localWindows and windowId != None:
        #    localWindows.append(windowId)
    localWindows = tConfig.getLocalWindowsFromMachineDesc(machineDesc)

    # return

    global fullRect
    fullRect = tConfig.getMainDisplayRect()
    if mpi.rank == 0:
        print "FULL DISPLAY:", fullRect.width, fullRect.height


def run():

    # not really working
    #sys.stdout = open( "output/%s.stdout" % mpi.rank, "w" )
    #sys.stderr = open( "output/%s.stderr" % mpi.rank, "w" )

    #debugFile.openfile("output/%s" % mpi.rank, "w") # of = open( "output/%s" % mpi.rank, "w" )
    #debugFile.write("begin\n")
    #debugFile.flush()
    #debugFile.write("%s\n"% sys.argv )
    #debugFile.flush()

    global tileConfig
    print "args:", sys.argv

    #streamProtocol = StreamProtocols.FLX_H261
    streamProtocol = StreamProtocols.CELERITAS_TCP_RAW

    # Parse options:
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                           default=None,
                     help="Specify a tiled display config file.")
    parser.add_option("", "--loadAllMovieTiles", action="store_true",
        dest="loadAllMovieTiles", default=False,
        help="Have all tiles load all movie tiles so movie can be dragged around.")
    parser.add_option("", "--allowFrameSkip", action="store_false",
        dest="allowFrameSkip", default=True,
        help="Allow movies to skip frames (automatic with --loadAllTiles).")
    parser.add_option("--stream", action="append", dest="stream",
                           default=None,
                     help="Specify a stream to receive.")
    parser.add_option("--groupedStream", action="append", dest="groupedStream",
                           default=None,
                     help="Specify a stream to receive.")
    parser.add_option("--hostnames", dest="hostnames",
                           default=None,
                     help="Force list of hostnames/confignames.  mpi id used to index the list.")
    parser.add_option("--streamColsRows", dest="streamColsRows", 
                           default=None,
                     help="Specify columns and rows for streams (in one/each network location).")
    parser.add_option("--streamGroupsColsRows", dest="streamGroupsColsRows", 
                           default=None,
                     help="Specify columns and rows for network locations.")
    parser.add_option("--scale", dest="movieScale", 
                           default=None,
                     help="Specify scale for movie playback.")
    parser.add_option("--sequence", action="append", dest="sequences", 
                           default=None,
                     help="Specify sequence of movies. (comma separated)")
    parser.add_option("--plant", dest="plant", action="store_true",
                           default=False,
                     help="Plant a stream so it can't move (allows streaming optimizations).")
    parser.add_option("--streamSize", action="append", dest="streamSize",
                           default=None,
                     help="Specify a stream size.")
    parser.add_option("--pos", action="append", dest="positions",
                           default=None,
                     help="Specify an object position.")
    parser.add_option("--layout", action="append", dest="layouts",
                           default=None,
                     help="Specify layout of objects.")
    parser.add_option("--movieLayout", action="append", dest="movieLayouts",
                           default=None,
                     help="Specify layout of tiles in a movie.")
    parser.add_option("--inputhost", dest="inputHost",
                           default="localhost",
                     help="Airstream server hostname.")
    parser.add_option("--inputport", dest="inputPort",
                           default=11000,
                     help="Airstream server port.")
    #parser.add_option("--streamRects", action="append", dest="streamRects",
    #                       default=None,
    #                 help="Specify streamRects.")

    options, sysArgs = parser.parse_args()

    allowFrameSkip=False
    if options.allowFrameSkip or options.loadAllMovieTiles:
        allowFrameSkip = True
    movieScale = None
    if options.movieScale != None:
        movieScale = options.movieScale.split("x")[:2]
        if len(movieScale) < 2:
            raise Exception("--scale option should be in this format: --scale=2.0x2.0")
        movieScale = float(movieScale[0]), float(movieScale[1])

    movieSequences = []

    if options.sequences != None:
        for sequence in options.sequences:
            paths = sequence.split(",")
            movieSequences.append(paths)

    if options.streamColsRows != None:
        options.streamColsRows = options.streamColsRows.split("x")
        options.streamColsRows = [ int(i) for i in options.streamColsRows ]
        if len(options.streamColsRows) < 2:
            raise Exception("--streamColsRows needs to be in the format \"3x2\"")
        #print "COLS ROWS:", options.streamColsRows, type(options.streamColsRows[0])
        #raise

    if options.streamGroupsColsRows != None:
        options.streamGroupsColsRows = options.streamGroupsColsRows.split("x")
        options.streamGroupsColsRows = [ int(i) for i in options.streamGroupsColsRows ]
        if len(options.streamGroupsColsRows) < 2:
            raise Exception("--streamGroupsColsRows needs to be in the format \"3x2\"")

    if options.streamSize != None:
        tmp = []
        for pair in options.streamSize:
            if len(pair.split("x")) != 2:
                raise Exception("--streamSize needs to be in the format \"600x400\" or \"600x400\",\"500x300\"")
            x,y = pair.split("x")
            tmp.append( (int(x),int(y)) )
        options.streamSize = tmp

    if options.positions != None:
        tmp = []
        for p in options.positions: 
            if len(p.split("x")) != 2:
                raise Exception("--pos needs to be in the format \"100x200\" or \"200x300\",\"100x300\"")
            x,y = p.split("x")
            tmp.append( (int(x),int(y)) )
        options.positions = tmp
    global gPositionsIndex
    gPositionsIndex = 0

    if (gFlxStreamingSupported and not gCeleritasStreamingSupported):
        options.streamSizes = [(352,288)]  # H.261 for now.

    print dir(options), type(options), options.__class__
    if hasattr(options, "config") and getattr(options, "config"):
        from configLoader import LoadConfigPy
        tileConfig = LoadConfigPy(getattr(options,"config"))
    else:
        raise Exception("Please specify the config file on the cmd-line with -c")
        # Older method:
        #if mpi.procs == 2:
        #    tileConfig = CreateLocal2TestConfig()
        #else:
        #    tileConfig = CreateLocalTestConfig()
        # SaveConfig(tileConfig, "amConfigTmp.txt")
        # tileConfig = LoadConfig("amConfigTmp.txt") # important to load from file so all nodes have the same tileIds.

    setupLocalConfig(tileConfig, options) 
    print gethostname(), machineDesc.hostname, localRects, absoluteRects
    
    #rects = [Rect(0,0,1280,1024), Rect(1280,0, 1280,1024)]
    #rects = [Rect(0,0,1280,1024)]

    if len(localWindows) == 0:
        os.environ["DISPLAY"] = ":0.0"
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        #windowWidth = 2560 # 1280# 320
        #windowWidth = 3840 # 1280# 320
        windowWidth = 2560 # 1280# 320
        windowHeight = 1024 # 1024 # 280
        #windowWidth = 1280 # 1280# 320
        #windowHeight = 1024 # 1024 # 280
        print "POSA:", os.environ['SDL_VIDEO_WINDOW_POS']
    else:
        
        # There is currently only one "localWindow" per process.
        #   All tiles are within the same localWindow. We can get get
        #   this window simply from any tile's config for a machine.
        os.environ["DISPLAY"] = localWindows[0].getDisplayStr()
        print "Local windows offset:", localWindows[0].getOffset()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%s,%s" % (localWindows[0].getOffset())
        print "POS:", os.environ['SDL_VIDEO_WINDOW_POS']
        windowWidth = localWindows[0].rect.width
        windowHeight = localWindows[0].rect.height

    # print gethostname(), mpi.rank, "DISPLAY SIZE:", windowWidth, windowHeight

    fullRightBoundary = fullRect.width

    #imageFilename = sys.argv[1]

    app = App(windowWidth, windowHeight)

    # app state contains a few things such as the exitFlag that 
    #    will be synced from the master state.
    app.state=AppState()
    app.state.exitNextFrame = False

    visualsManager = VisualsManager()

    ### Setup Renderers
    renderers = []
    for i in range(len(localRects)):
        displayRect  = localRects[i]
        if i == 0:
            renderer = glRenderer2D(multipleRenderers=True, firstRenderer=True)
            #renderer.addFrameSetupObj(ScreenClearer(color=(.9, .4, .4), clearDepth=False))
            renderer.addFrameSetupObj(ScreenClearer(color=(.0, .0, .0), clearDepth=False))
        else:
            renderer = glRenderer2D(multipleRenderers=True)
            #renderer.addFrameSetupObj(ScreenClearer(color=(.4, .9, .4), clearDepth=False))
            renderer.addFrameSetupObj(ScreenClearer(color=(.0, .0, .0), clearDepth=False))
        renderers.append(renderer)
        app.addRenderer(renderer)

    app.initialize(windowBorder=False)
    #app.initialize(windowBorder=True)
    pygame.mouse.set_visible(False)

    for i in range(len(localRects)):
        print "SETTING RECT:", localRects[i]
        renderers[i].init(app.width, app.height, viewportRect=localRects[i])


    visualsManager.setRenderers(renderers)


    #box = glBox()
    #app.addDynamicObject(box)
    glEnable(GL_TEXTURE_2D)
    masterObjects = []
    objectsListList = [] # first object in each tuple on master node is source for all others

    #for i in range(len(renderers)):
    def CreateObj(imageFilename, imagePos=(2000,500), obj=None, scale=None, objDesc=None, gridColsRows=None, netGridColsRows=None, plant=False):
      if None == objDesc:
        objDesc = ObjDesc(ObjType.UNSPECIFIED)
      boxes = []
      for i in range(len(renderers)):
        absRect = absoluteRects[i]
        locRect = localRects[i]
        renderer = renderers[i]
        if obj == None:
            if objDesc.type == ObjType.STREAM:
                #box = CreateTileDisplayStreamObject(imageFilename, screenRect=Rect(0,0,locRect.width, locRect.height), pos=imagePos, absRect= absRect, fullRect=fullRect, blend=True, scale=scale)
                box = CreateGroupTileDisplayStreamObject(imageFilename, objDesc, screenRect=Rect(0,0,locRect.width, locRect.height), pos=imagePos, absRect= absRect, fullRect=fullRect, blend=True, scale=scale, gridColsRows=gridColsRows)
            elif objDesc.type == ObjType.GROUPED_STREAM:
                try:
                    box = CreateMultiNetGroupTileDisplayStreamObject(imageFilename, objDesc, screenRect=Rect(0,0,locRect.width, locRect.height), pos=imagePos, absRect= absRect, fullRect=fullRect, blend=True, scale=scale, gridColsRows=gridColsRows, netGridColsRows=netGridColsRows, plant=plant )
                except:
                    traceback.print_exc()
                    sys.exit()
            elif objDesc.type == ObjType.TILED_MOVIE_WITH_LAYOUT:
                try:
                    box = CreateTiledMovieObjectFromLayout(imageFilename, screenRect=Rect(0,0,locRect.width, locRect.height), pos=imagePos, absRect= absRect, fullRect=fullRect, loadAllMovieTiles=options.loadAllMovieTiles, scale=scale, allowFrameSkip=allowFrameSkip)
                except:
                    import traceback
                    traceback.print_exc()
                    sys.exit()
            else: # objDesc.type.UNSPECIFIED
                #box = glTxtrBox(imageFilename, screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=imagePos, absRect= absRect, fullRect=fullRect, blend=True)
                box = CreateTileDisplayObject(imageFilename, screenRect=Rect(0,0,locRect.width, locRect.height), pos=imagePos, absRect= absRect, fullRect=fullRect, blend=True, loadAllMovieTiles=options.loadAllMovieTiles, scale=scale, allowFrameSkip=allowFrameSkip)
        else:
            box = obj


        # to scale, change the geometry and the txtr coords: imageSize and
        #box.imageSize = (box.imageSize[0]*2, box.imageSize[1]*2)

        #box.easyTexture.zoom(5,1)

        #box.easyTexture.setOffset( (absRect.x % float(box.easyTexture.getWidth())) / box.easyTexture.getWidth(),
        #                           (absRect.y % float(box.easyTexture.getHeight())) / box.easyTexture.getHeight() )

        # box.easyTexture.setWidth( float(locRect.width) / float(box.easyTexture.getHeight()) )

        #zoom = (0.5,1)
        #box.easyTexture.setZoom(zoom[0], zoom[1])
        #box.easyTexture.setOffset(absRect.x * zoom[0] ,absRect.y * zoom[1])
        #box.easyTexture.setZoom(float(box.easyTexture.getWidth()) / localRect.width,
        #                        float(box.easyTexture.getHeight()) / localRect.height )
        # scale offset back by zoom   (offset is between 0 and 1)
        #box.easyTexture.setOffset( float(rect.x) / fullRect.width * box.easyTexture.getWidth(),
        #                           float(rect.y) / fullRect.height * box.easyTexture.getHeight())

        app.addDynamicObject(box, addToRenderer=False)
        renderers[i].addDynamicObject(box)
        boxes.append(box)

        if i == 0 and mpi.rank == 0:
            masterObjects.append(box)

      if objDesc.type==ObjType.STREAM: # setup network reception for one machine
          if StreamProtocols.FLX_H261 == streamProtocol:
              from streamView import StreamView, StartStreamViewLoop, StreamState
          elif StreamProtocols.CELERITAS_TCP_RAW == streamProtocol:
              from streamViewCeleritas import StreamView, StartStreamViewLoop, StreamState
          else:
              raise Exception("Unhandled stream format: %s" % streamProtocol)
          numStreamStates = boxes[0].getNumStreams()
          streamStateList = []
          for i in range(numStreamStates):
              streamState = StreamState()
              streamState.printInterval = 0 # disable extra prints for now
              streamStateList.append(streamState)
          def nop(nameList):
              pass
          #streamStateList = [streamState]
          address = imageFilename

          if StreamProtocols.FLX_H261 == streamProtocol:
              StartStreamViewLoop(address, streamStateList, [ x.reorder for x in boxes ])  #call reorder on each group stream obj
          else: # CELERITAS_RAW_TCP for now
              address, streamPort = address.split("/")
              streamPort = int(streamPort)
              StartStreamViewLoop(address, streamPort, objDesc.streamWidth, objDesc.streamHeight, streamStateList, [ x.reorder for x in boxes ])  #call reorder on each group stream obj
          for box in boxes:  # add the gui objects for each display on the machine.
              box.setStreamState(streamStateList)
      elif objDesc.type==ObjType.GROUPED_STREAM: # setup network reception for one machine
          if StreamProtocols.FLX_H261 == streamProtocol:
              from streamView import StreamView, StartStreamViewLoop, StreamState
          elif StreamProtocols.CELERITAS_TCP_RAW == streamProtocol:
              from streamViewCeleritas import StreamView, StartStreamViewLoop, StreamState
          else:
              raise Exception("Unhandled stream format: %s" % streamProtocol)
          # Want to avoid creating duplicate streamStates for the same address
          #   keep a dict of address -> streamState
          print "ADDRESS:", imageFilename
          addressStateDict = {}  # address: streamStateList
          addressReorderCallbacks = {}  # address: [callbacks]
          for box in boxes:  # add the gui objects for each display on the machine.
              for child in box.getChildren(): #box is a GroupObject holding GroupTiledStreamObject
                  # creating stream states for children
                  if isinstance(child, GroupTiledStreamObject):
                      numStreamStatesForChild = child.getNumStreams() # num streams per net conn.
                      if child.address not in addressStateDict:
                          streamStateList = []
                          for i in range(numStreamStatesForChild):
                              streamState = StreamState()
                              streamState.printInterval = 0 # disable extra prints for now
                              streamStateList.append(streamState)
                          def nop(nameList):
                              pass
                          # store streamStateList for network address
                          addressStateDict[child.address] = streamStateList
                          if child.address not in addressReorderCallbacks:
                              addressReorderCallbacks[child.address] = []
                      else:
                          streamStateList = addressStateDict[child.address]

                      # store reorder callback for this object
                      addressReorderCallbacks[child.address].append(child.reorder)
                  #else:
                  #    pass # Null placeholder object, don't setup a stream
          #for address,streamStateList in addressStateDict.items():
          for address in imageFilename:  # import to iterate through addresses in this order
              if address in addressStateDict:
                  streamStateList = addressStateDict[address]
                  reorderCallbacks = addressReorderCallbacks[address]
                  print "***** STARTING:|%s|"% address, type(address)
                  #time.sleep(0.1) # FIXME, intead, need add a "ready" callback from 
                                  # pyRTP once thread is setup.
                  #time.sleep(0.1)
                  address, streamPort = address.split("/")
                  streamPort = int(streamPort)
                  StartStreamViewLoop(address, streamPort, objDesc.streamWidth, objDesc.streamHeight, streamStateList, reorderCallbacks)  #call reorder on each group stream obj

          for box in boxes:
              for child in box.getChildren():
                  if isinstance(child, GroupTiledStreamObject):
                      streamStateList = addressStateDict[child.address]
                      child.setStreamState(streamStateList)


      print "CREATED OBJS:", len(boxes), boxes

      return boxes

    """
    obj = CreateObj(imageFilename, (0,0))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/public_html/vl3/20071116/B/Screenshot-VL3 Application-B0250.png", imagePos=(3200,400))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/public_html/vl3/20071116/A/Screenshot-VL3 Application-600.png", imagePos=(800,1700))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/public_html/vl3/20070123/vl3_20070123_142002.png", imagePos=(100,800))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/public_html/vl3/20061109/vl3_20061109_161226.png", imagePos=(4500,2000))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/public_html/vl3/20080402paper/vl3_nodes.png", imagePos=(0,0))
    objectsListList.append(obj)
    obj = CreateObj("/home/eolson/am-macs/data/pic8.png", imagePos=(4200,0))
    #obj = CreateObj("/home/eolson/am-macs/data/trim.png", imagePos=(4200,0))
    objectsListList.append(obj)
    """

    #imageDir = '/homes/turam/tiledDisplayImages'
    #imageDir = '/homes/eolson/am-macs/data/images'
    #defaultImageDir = '/homes/eolson/am-macs/data/largeImages'
    defaultImageDir = '/homes/eolson/data/largeImages'
    #imageDir = '/home/eolson/am-macs/data/kuhlmann'
    imageDir=None

    # let command line arg override the image path.
    #if len(sys.argv) > 1 and os.path.exists(sys.argv[1]): #  and os.path.isdir(sys.argv[1]):
    #    imageDir = sys.argv[1]
    if len(sysArgs) > 0 and os.path.exists(sysArgs[0]): #  and os.path.isdir(sys.argv[1]):
        imageDir = sysArgs[0]

    if options.stream == None and options.groupedStream == None and imageDir == None:
        imageDir = defaultImageDir  # make sure we try to show something on the screen.

    print "image path to load:", imageDir

    def IsValidDataType(path):
        recognizedExtensions = ["png", "jpg", "jpeg", "tif", "tiff", "tga", "gif", "rgb", "rgba", "sgi", "mpg", "mp4", "mov", "vob", "ogv", "avi", "tdmovie"]
        extension = (path.split(".")[-1]).lower()

        if extension in recognizedExtensions and not path.startswith("._"):
            return True
        else:
            return False

    def loadImageOrMovie(objPath, pos=None):
        if None == objPath:
            return None
        thisObjScale = movieScale
        if "NOAA_TEST.tdmovie" in objPath: # FIXME, add per object scale options
            thisObjScale = [2.0, 2.0]
        elif "HeadHeartLiver2.tdmovie" in objPath:
            thisObjScale = [1.2, 1.2]
        elif "jai-head2.mp4" in objPath:
            thisObjScale = [3.0, 3.0]
        elif "FOAM.tdmovie" in objPath:
            thisObjScale = [1.8, 1.8]
        #elif "NEW_DWARF.tdmovie" in objPath:
        #    thisObjScale = [2.0, 2.0]
        #elif "VORTICITY.tdmovie" in objPath:
        #    thisObjScale = [2.0, 2.0]
        elif "FUZZY.tdmovie" in objPath:
            thisObjScale = [2.0, 2.0]
        #elif "FISCHER.tdmovie" in objPath:
        #    thisObjScale = [2.0, 2.0]
        #elif "DWARF.tdmovie" in objPath:
        #    thisObjScale = [2.0, 2.0]
        elif "BGL.tdmovie" in objPath:
            thisObjScale = [2.0, 2.0]
        elif "enzo-b4096_2.tdmovie" in objPath:
            thisObjScale = [1.4, 1.4]
        elif "Enzo-4096-Evo-res4096x2304.tdmovie" in objPath:
            thisObjScale = [1.4, 1.4]
        elif "Enzo-4096-SC09-res4096x2304.tdmovie" in objPath:
            thisObjScale = [1.3, 1.3]
        elif "fischer_movie01.tdmovie" in objPath:
            thisObjScale = [1.0, 1.0]
            #if None == options.positions:
            #    options.positions = [ (0, -1000) ]
        elif "FISCHER_MOVIE01" in objPath:
            if None == options.positions:
                options.positions = [ (0, -100) ]
        #elif "enzo-b4096" in objPath:
        #    thisObjScale = [2.0, 2.0]
        if objPath != None and os.path.exists(objPath):
            if IsValidDataType(objPath):  # some data types are directories
                print "Creating Obj:", objPath
                #if None == pos:
                #    pos = (0,30)
                if IsTiledMoviePath(objPath):
                    movieDims = GetTiledMoviePathDims(objPath)
                    # center obj since there's only one
                    if thisObjScale != None:
                        #pos = [2500 + fullRect.width / 2 - movieDims[0] / 2 * movieScale[0], fullRect.height / 2  - movieDims[1] / 2 * movieScale[1]]
                        if None == pos:
                            pos = [fullRect.width / 2. - movieDims[0] / 2. * thisObjScale[0], fullRect.height / 2.  - movieDims[1] / 2. * thisObjScale[1]]
                        else:
                            print "Pos is not None, not recentering movie"
                    else:
                        if None == pos:
                            pos = [fullRect.width / 2. - movieDims[0] / 2., fullRect.height / 2. - movieDims[1] / 2.]
                    print "Recentered Movie position is:", pos, "movieDims:", movieDims, "full display rect:", fullRect
                elif IsImagePath(objPath):
                    f = Image.open(objPath)
                    imageDims = f.size
                    if None == pos:
                        pos = [fullRect.width / 2 - imageDims[0] / 2, fullRect.height / 2 - imageDims[1] / 2]
                print "SCALE !!!", thisObjScale
                obj = CreateObj(objPath, imagePos=pos, scale=thisObjScale)
                if obj != None:
                    objectsListList.append(obj)
            else: 
                print "Path is not to a single data file/data item"
                if os.path.isdir(objPath):
                    imageList = os.listdir(objPath)
                else: # just one image
                    imageList = [objPath]
                    objPath = ""
                print "File List:", imageList
                j = 0
                imageList.sort()
                for i in imageList:
                    extension = i.split(".")[-1]
                    # just guesses so far
                    #if extension.lower() in ["png", "jpg", "jpeg", "tif", "tiff", "tga", "gif", "rgb", "rgba", "sgi", "mpg", "mp4", "mov", "vob", "ogv"] and not i.startswith("._"):
                    if IsValidDataType(i):
                        #obj = CreateObj(os.path.join(objPath,i), imagePos=(3000-j*300,2000-j*200))
                        pos = (100+j*220,30+j*0)
                        fullPath = os.path.join(objPath, i)
                        if IsTiledMoviePath(fullPath):
                            movieDims = GetTiledMoviePathDims(fullPath)
                            # center tiled movies for now
                            pos = [fullRect.width / 2 - movieDims[0] / 2, fullRect.height / 2 - movieDims[1] / 2]
                        print "Creating Obj:", fullPath
                        obj = CreateObj(fullPath, imagePos=pos, scale=thisObjScale)
                        #obj = CreateObj(os.path.join(objPath,i), imagePos=(0+j*220,0+j*0))
                        if obj != None:
                            objectsListList.append(obj)
                            j += 1
                    else:
                        print "skipping file (unhandled extension):", i

            return obj

    def loadMovieSequence(moviePaths):
        if len(movieSequence) > 1:
            sequenceObj = MovieSequence()
        else:
            sequenceObj = None

        for moviePath in movieSequence:
            obj = loadImageOrMovie(moviePath)
            if None != sequenceObj:
                numLoops = 1
                if "NOAA_TEST.tdmovie" in moviePath:
                    numLoops = 5
                sequenceObj.append(obj, numLoops)
        if None != sequenceObj:
            sequenceObj.initializeObjects()
            return sequenceObj

    def loadLayout(layoutPath):
       layoutEntries = ReadLayout(layoutPath)  
       for entry in layoutEntries:
           loadImageOrMovie(entry.path, pos=entry.pos)

    def getNextPosition():
        global gPositionsIndex
        if None != options.positions and gPositionsIndex < len(options.positions):
            tmpPos = options.positions[gPositionsIndex]
            gPositionsIndex+=1
            return tmpPos
        return None

    # load movie layout if specified
    if options.movieLayouts != None:
        thisObjScale = movieScale
        for movieLayout in options.movieLayouts:
            pos = getNextPosition()
            obj = CreateObj(movieLayout, imagePos=pos, scale=thisObjScale, objDesc=ObjectDescription(ObjType.TILED_MOVIE_WITH_LAYOUT))
            if obj != None:
                objectsListList.append(obj)

    # load layout if specified
    if options.layouts != None:
        for layout in options.layouts:
            loadLayout(layout)

    # load image path if specified (different from default)
    if imageDir != defaultImageDir:
        loadImageOrMovie(imageDir, getNextPosition())
    elif 0 == len(movieSequences) and None == options.layouts and None == options.movieLayouts:  # or load default if no extra options 
                                    #   were specified.
        loadImageOrMovie(imageDir, getNextPosition()) # default

    if len(movieSequences) > 0:  # load sequences from --sequence
        for movieSequence in movieSequences:
            sequenceObj = loadMovieSequence(movieSequence)
            app.addDynamicObject(sequenceObj, addToRenderer=False)


    #print "******************", options.stream
    if options.stream != None:
        if not gStreamingSupported:
            raise Exception("Error using --stream.  Streaming not supported.  Make sure StreamView could be imported.")
        try:
            address = options.stream[0]
            if len(options.stream) > 1:
                print "WARNING: So far we only handle one stream address. (multiple stream address handling coming soon)"
            #from streamView import StreamView, StartStreamViewLoop
            #streamView = StreamView()
            #obj = CreateObj(None, imagePos=(0, 0), obj=streamView)
            #objectsListList.append(obj)
            #StartStreamViewLoop(address)
            pos = [fullRect.width / 2, fullRect.height / 2 ]
            print "*********POS:", pos, "from:", fullRect
            streamWidth = options.streamSize[0][0]
            streamHeight = options.streamSize[0][1]
            vflip=False # works for RAW
            if StreamProtocols.FLX_H261 == streamProtocol:
                vflip=True
            streamDesc = objDesc=StreamObjDescription(streamProtocol, (streamWidth,streamHeight), vflip=vflip )
            obj = CreateObj(address, imagePos=pos, objDesc=streamDesc, scale=movieScale, gridColsRows=options.streamColsRows)
            if obj != None:
                objectsListList.append(obj)

        except Exception, e:
            traceback.print_exc()

    if options.groupedStream != None:
        if not gStreamingSupported:
            raise Exception("Error using --groupedStream.  Streaming not supported.  Make sure StreamView could be imported.")
        try:
            if len(options.groupedStream) > 1:
                print "FOR NOW only one group of addresses. (Only specify --groupedStream once.): ", options.groupedStream
                sys.exit()
            if mpi.rank == 0:
                print "GROUP STREAM: ", options.streamGroupsColsRows, options.streamColsRows
            options.groupedStream = options.groupedStream[0]
            addresses = options.groupedStream.split(",")
            pos = [fullRect.width / 2, fullRect.height / 2 ]
            print "*********POS:", pos, "from:", fullRect
            if (options.streamGroupsColsRows == None):
                print "need to specify --streamGroupsColsRows, when using --groupedStream"
                sys.exit()
            try:
                streamWidth = options.streamSize[0][0]
                streamHeight = options.streamSize[0][1]
                vflip=False # works for RAW
                if StreamProtocols.FLX_H261 == streamProtocol:
                    vflip=True
                streamDesc = GroupedStreamObjDescription(streamProtocol, (streamWidth,streamHeight), vflip=vflip)
                obj = CreateObj(addresses, imagePos=pos, objDesc=streamDesc, scale=movieScale, gridColsRows=options.streamColsRows, netGridColsRows=options.streamGroupsColsRows, plant=options.plant)
            except:
                traceback.print_exc()
                sys.exit()
            if obj != None:
                objectsListList.append(obj)

        except Exception, e:
            traceback.print_exc()
    app.drawBounds = 0



    #class Cursor:
    def CreateCursor(x=500,y=500, xvel=100, yvel=100, imageName="data/fl-logo-color-small.gif"):
        tmpCursors = []
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            cursor = glTxtrBox(imageName, screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(x,y), absRect= absRect, fullRect=fullRect)
    
            app.addDynamicObject(cursor, addToRenderer=False)
            renderers[i].addDynamicObject(cursor)
            tmpCursors.append(cursor)
    
            # change this to only happen on master and sync
            if mpi.rank == 0:
                app.addDynamicObject(CursorAutoMover(cursor, xrange=(0, fullRect.width), yrange=(0, fullRect.height), xvel=xvel, yvel=yvel), addToRenderer=False)
        return tmpCursors

    #numCursors = 3 
    numCursors = 0 
    cursorListList = []
    for i in range(numCursors): 
        nodeCursors = CreateCursor(x=randrange(0,fullRect.width), y=randrange(0,fullRect.height),
                     xvel=randrange(200,400), yvel=randrange(200,400))
        cursorListList.append(nodeCursors)

    # Now the first mouse cursor
    if 1: # "wii" in sys.argv:
        tmpCursors = []
        masterCursor = None
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            firstCursor = glTxtrBox("data/arrow2_white.png", screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(fullRightBoundary,500), absRect= absRect, fullRect=fullRect, blend=True)
            if mpi.rank == 0 and i == 0:
                masterCursor = firstCursor
            
            app.addDynamicObject(firstCursor, addToRenderer=False)

            renderers[i].addDynamicObject(firstCursor)
            tmpCursors.append(firstCursor)
        cursorListList.append(tmpCursors)

    # Now the second mouse cursor
    if 1: # "wii2" in sys.argv:
        tmpCursors = []
        masterCursor2 = None
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            secondCursor = glTxtrBox("data/arrow1_green.png", screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(fullRightBoundary,500), absRect= absRect, fullRect=fullRect, blend=True)
            if mpi.rank == 0 and i == 0:
                masterCursor2 = secondCursor
            
            app.addDynamicObject(secondCursor, addToRenderer=False)

            renderers[i].addDynamicObject(secondCursor)
            tmpCursors.append(secondCursor)
        cursorListList.append(tmpCursors)
        # end second mouse cursor

    if 1: # "wii3" in sys.argv:
        tmpCursors = []
        masterCursor3 = None
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            thirdCursor = glTxtrBox("data/arrow1_yellow.png", screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(fullRightBoundary,500), absRect= absRect, fullRect=fullRect, blend=True)
            if mpi.rank == 0 and i == 0:
                masterCursor3 = thirdCursor
            app.addDynamicObject(thirdCursor, addToRenderer=False)
            renderers[i].addDynamicObject(thirdCursor)
            tmpCursors.append(thirdCursor)
        cursorListList.append(tmpCursors)
        # end third mouse cursor

    if 1: # "wii4" in sys.argv:
        tmpCursors = []
        masterCursor4 = None
        for i in range(len(renderers)):
            absRect = absoluteRects[i]
            locRect = localRects[i]
            renderer = renderers[i]
            fourthCursor = glTxtrBox("data/arrow1_red.png", screenRect=Rect(0,0,locRect.width, locRect.height), imagePos=(fullRightBoundary,500), absRect= absRect, fullRect=fullRect, blend=True)
            if mpi.rank == 0 and i == 0:
                masterCursor4 = fourthCursor
            app.addDynamicObject(fourthCursor, addToRenderer=False)
            renderers[i].addDynamicObject(fourthCursor)
            tmpCursors.append(fourthCursor)
        cursorListList.append(tmpCursors)
        # end fourth mouse cursor

    objectsListList += cursorListList

    # print mpi.rank, " cursor list:", cursorListList
    #syncer = Syncer(cursorListList)
    if mpi.procs > 1:
        syncer = Syncer(objectsListList)
        app.addDynamicObject(syncer, addToRenderer=False)

    data = {}

    groupedTileMovies = []
    movieSequenceObjects = []
    for objectsList in objectsListList:
        for object in objectsList:
            if isinstance(object, TiledMovieGroupObject):
                groupedTileMovies.append(object)
            elif isinstance(object, MovieSequence):
                movieSequenceObjects.append(object)

    class RenderOrder:
        def __init__(self):
            self.order = range(1, 26) # [1,2,3,4,5,6,7,8]

        def storeDataInDict(self, dataDict):
            self.order = renderers[0].getRenderOrder()
            dataDict["order"] = self.order

        def setDataFromDict(self, data):
            self.order =data["order"]

    renderOrder = RenderOrder()
    dataSources = [renderOrder] + groupedTileMovies + movieSequenceObjects + [app.state]

    def updateProc():
        if mpi.rank == 0:
            global gProfile
            if gProfile != None:
                global gProfileCount
                gProfileCount += 1
                if gProfileCount > 100:
                    print "dumping stats to out.prof"
                    gProfile.dump_stats("out.prof")
                    gProfileCount = 0

    def checkForQuit():
        # check app.state.getFlagToExit() to see if we should quit
        if mpi.procs > 1: # need to do an mpi exit
            if app.state.getFlagToExit():
                if mpi.rank == 0:
                    print mpi.rank, "Quitting mpi app."
                print "Exiting from proc", mpi.rank
                mpi.abort() # for mpi apps, app terminates here.
        else: # 1 proc
            #print "EXIT next frame:", app.state.exitNextFrame
            if app.state.getFlagToExit():
                # No need to communicate to slaves to exit next frame, exit now
                print "Quitting single process app."
                app.quit()           

    def receivedSyncedData(resultData): # isn't called for rank == 0
        # Data was just sent to slaves from the master.  Apply this 
        #   master state to objects.  To do this, we call setDataFromDict()
        #   on objects that we know use synced state.

        #if mpi.rank == 1:
        #    print resultData
        renderOrder.setDataFromDict(resultData)
        for renderer in renderers:
            renderer.setRenderOrder(renderOrder.order)
        for gtm in groupedTileMovies:
            gtm.setDataFromDict(resultData)
        app.state.setDataFromDict(resultData)


    # A more flexible and generic syncer
    #   objects implement storeDataInDict, master broadcasts the dict,
    #   receivedSyncedData processes it for us, calling obj.setDataFromDict(d).
    if mpi.procs > 1:
        genSyncer = GenericSyncer(data, updateCallback=receivedSyncedData, dataSources=dataSources)
        app.addDynamicObject(genSyncer, addToRenderer=False)

    # Create a simple object to get an update() call each frame
    #   Future: something like app.addUpdateCallback(c) could be simpler
    class SimpleUpdater:
        # Call a few tasks to be done each frame
        def __init__(self): pass    

        def update(self, secs, app):
            updateProc()
            checkForQuit()
    app.addDynamicObject(SimpleUpdater(), addToRenderer=False)
    

    configUI = ConfigUI( tileConfig=tileConfig )
    if mpi.procs > 1:
        syncer.addDataObj(configUI)


    moteManager = None


    mote = None

    moteIds=['00:1E:A9:4F:59:8E', '00:1E:35:CE:6D:4D', '00:1E:35:CE:DE:74', '00:1E:A9:4F:58:29']
    #moteIds=['00:1E:35:CE:6D:4D', '00:1E:A9:4F:59:8E', '00:1E:35:CE:DE:74', '00:1E:A9:4F:58:29']
    #moteIds=['00:1E:35:CE:DE:74', '00:1E:A9:4F:58:29', '00:1E:35:CE:6D:4D', '00:1E:A9:4F:59:8E']
    #moteIds=['00:1E:A9:4F:58:29', '00:1E:35:CE:6D:4D', '00:1E:35:CE:DE:74', '00:1E:A9:4F:59:8E']

    if mpi.rank == 0:
        for arg in sys.argv:
            if "wii" == arg.lower():
                #mote, moteMouse, tileMote = SetupMoteControl(masterCursor, app, fullRect.width, fullRect.height, moteId="00:17:AB:32:BF:EF", leds=(1,0,0,0))
                # FIXME: organize better so not so many arguements are needed
                mote, moteMouse, tileMote = SetupMoteControl(masterCursor, app, fullRect.width, fullRect.height, moteId=moteIds[0], leds=(1,0,0,0), renderers=renderers, configUI=configUI, masterObjects=masterObjects, moteManager=moteManager)
            if "wii2" == arg.lower():
                #mote2, moteMouse2, tileMote2 = SetupMoteControl(masterCursor2, app, fullRect.width, fullRect.height, moteId="00:19:1D:79:93:E0", leds=(0,1,0,0), renderers=renderers, configUI=configUI, cursorListList=cursorListList)
                mote2, moteMouse2, tileMote2 = SetupMoteControl(masterCursor2, app, fullRect.width, fullRect.height, moteId=moteIds[1], leds=(0,1,0,0), renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=moteManager)
            if "wii3" == arg.lower():
                mote3, moteMouse3, tileMote3 = SetupMoteControl(masterCursor3, app, fullRect.width, fullRect.height, moteId=moteIds[2], leds=(0,0,1,0), renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=moteManager)
            if "wii4" == arg.lower():
                mote4, moteMouse4, tileMote4 = SetupMoteControl(masterCursor4, app, fullRect.width, fullRect.height, moteId=moteIds[3], leds=(0,0,0,1), renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList, moteManager=moteManager)


        if gWiiSupported == True and "wii" not in sys.argv:
            cursors=[masterCursor, masterCursor2, masterCursor3, masterCursor4]
            # FIXME: organize better so not so many arguements are needed
            moteManager = MoteManager(app, fullRect, cursors, renderers=renderers, configUI=configUI, masterObjects=masterObjects, cursorListList=cursorListList)
            moteDetector = MoteDetector(numToConnect=1, detectedCallback=moteManager.newMoteDetected, getAlreadyConnectedIdsCallback=moteManager.getAlreadyConnectedIds)
            moteManager.setMoteDetector(moteDetector)
            moteDetector.startInThread()
            app.addDynamicObject(moteManager, addToRenderer=False)

    visualsManager.setObjectListListByRef(objectsListList)
    visualsManager.setMasterObjectListByRef(masterObjects)
    visualsManager.setCursorListList_tmpFunc(cursorListList)

    if mpi.procs > 1:
        mpi.barrier()

        if 0 == mpi.rank:
            print "******** simple position syncer, cursor objects:", syncer.cursors, "data objects", syncer.dataObjList
            print "******** GenericSyncer example sync dict:", genSyncer.getSyncExampleDict()

    print "Running app"


    def debugTestA():
        print "DEBUG TESTA", mpi.rank
    def debugTestB():
        print "DEBUG TESTB", mpi.rank
    debugTestA()
    app.callLater(0.0, debugTestB, [] )
    try:
        if (0 == mpi.rank):
            try:
                from input.airstreamInputAndEventProcessor import AirstreamInputAndEventProcessor
                inputAndEventProcessor = AirstreamInputAndEventProcessor(fullRect, app=app, visualsManager=visualsManager, host=options.inputHost, port=int(options.inputPort) )
                app.callLater(0.5, inputAndEventProcessor.initialize, [] )
                app.runWithTwisted()
            except:
                import traceback
                traceback.print_exc()
                print "WARNING: Cannot import input library.  Won't listen for controlling devices."
                app.run()
        else:
            app.run()
    except:
        #debugFile.write(traceback.format_exc() + "\n")
        #debugFile.flush()
        import traceback
        traceback.print_exc()
    finally:
        if mpi.rank == 0:
            if mote != None:
                mote.disconnect()
                if mote.readThread != None:
                    print "Exiting, joining thread"
                    mote.readThread.join()



if __name__ == "__main__":
    try:
        run()
    except:
        #debugFile.write(traceback.format_exc() + "\n")
        #debugFile.flush()
        raise
    """
    if mpi.rank == 0:
        from cProfile import Profile
        import time
        global gProfile
        gProfile = Profile(time.time)
        try:
            print "Run is:", run, dir(run), run.__module__
            gProfile.run("run()" )
        except:
            import traceback
            traceback.print_exc()
            pass
        print "saving stats to out.prof"
        gProfile.dump_stats("out.prof")

    else:
        run()
    """

