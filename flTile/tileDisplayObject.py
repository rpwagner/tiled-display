from glUtils import glTxtrBox, GetMaxTextureSize, glStreamedTxtrBox
from baseTileDisplayObject import BaseTileDisplayObject , NullTileDisplayObject
from groupObject import GroupObject
from groupTiledStreamObject import GroupTiledStreamObject
from flapp.pmath.rect import Rect
from flapp.pmath.vec2 import Vec2
from movieTileDisplayObject import IsMovieFile, IsTiledMoviePath, TiledMovieObject, CreateDumbMovieObjectOnEachTile, TiledMovieGroupObject, IsTiledMovieChunkImageBased
from layoutReader import ReadLayout
import Image
import math
import os

SupportedImageFormats = ["png", "jpg", "jpeg", "tif", "tiff", "tga", "gif", "rgb", "rgba", "sgi"]

def IsImagePath(path):
    if os.path.isfile(path) and os.path.splitext(path)[1].lower().strip(".") in SupportedImageFormats:
        return True
    else:
        return False

def CreateMovieObject(filename, screenRect, pos, absRect, fullRect, fps=None, scale=None, allowFrameSkip=None):
    return TiledMovieObject(filename=filename, screenRect=screenRect, absRect=absRect, fullRect=fullRect, pos=pos, fps=fps, scale=scale, allowFrameSkip=allowFrameSkip)
    #return CreateDumbMovieObjectOnEachTile(filename, pos)

def ReadTiledMovieDescription(path):
    description = open(os.path.join(path, "description.txt")).read()
    print "read description:", description

    des = {}   # {"tileColsRows":(1,1), fullRes:(1,1), tileRes:(1,1)}
    des["duration"]=None  # in case it's not specified
    des["FPS"]=None       # in case it's not specified

    for line in description.split("\n"):
        print "LINE:", line
        if len(line.strip()) > 0:
            #descriptionList = description.split(":")
            print "LINE:", line
            name, value = line.split(":")
            name = name.lower().strip()
            value = value.lower().strip()

            def parseTwoIntegerString(strng):
                x,y = value.split("x")
                return int(x), int(y)
            
            if name.startswith("tiles"):
               des["tileColsRows"]= parseTwoIntegerString(value)
            elif name.startswith("fullres"):
                des["fullRes"]= parseTwoIntegerString(value)
            elif name.startswith("tileres"):
                des["tileRes"] = parseTwoIntegerString(value)
            elif name.startswith("fps"):
                des["FPS"] = float(value)
            elif name.startswith("duration"):
               des["duration"]= float(value)
            elif len(name) == 0:
                pass
            else:
                print("warning, unrecognized line in tdmovie description.txt:", line, "NAME:", name)
    print "Read tdmovie description:", des
    return des
 
def GetTiledMoviePathDims(path):
    desc = ReadTiledMovieDescription(path)
    if "fullRes" in desc:
        return desc["fullRes"]
    else:
        raise Exception("Unabled to read resolution information from tiled movie description file.")

def CreateTiledMovieObjectFromLayout(layoutFile, screenRect, pos, absRect, fullRect, loadAllMovieTiles=False, scale=None, allowFrameSkip=None):
    print "CreateTiledMovieObjectFromLayout"

    objectsToGroup = []
    if None == pos:
        pos = (0, 0)

    layoutEntries = ReadLayout(layoutFile)  
    for entry in layoutEntries:
            moviePos = Vec2(pos[0] + entry.pos[0], pos[1] + entry.pos[1])

            movieRenderRect = Rect(moviePos[0], moviePos[1], entry.getWidth(), entry.getHeight())
            tileObject = None

            # same code as below func
            if loadAllMovieTiles or movieRenderRect.colliderect(absRect):
                movieTileFilename = entry.path
                fullMovieTilePath = movieTileFilename # for now has absolute paths

                # same code as below function
                print "movieTileFilename:", movieTileFilename, len(movieTileFilename)
                if len(movieTileFilename.strip()) > 0:
                    print "movieTileFilename:", movieTileFilename, len(movieTileFilename)
                    print "TiledMovie: loading tile: ", fullMovieTilePath
                    # obj.pos and obj.size will be used to group movie tiles.
                    fps = fps=entry.getProperty("fps")
                    tileObject = CreateMovieObject(fullMovieTilePath, screenRect, moviePos, absRect, fullRect, fps=fps, scale=scale, allowFrameSkip=allowFrameSkip)
                else:
                   print "Warning movieTile not found for:", xIndex, yIndex

            if not tileObject:
                tileObject = NullTileDisplayObject(pos=moviePos,size=(movieRenderRect.width,movieRenderRect.height) ) # Empty object to represent
                                                     # objects on other nodes
                                                 # and keep object list synced.
            objectsToGroup.append(tileObject)

    shortName = os.path.basename(layoutFile.strip(os.path.sep))
    duration = layoutEntries[0].getProperty("duration")
    fps = fps=layoutEntries[0].getProperty("fps")
    groupObject = TiledMovieGroupObject(shortName, objectsToGroup, duration=duration, fps=fps)

    groupObject.doChildUpdates=True
    returnObj = groupObject
    return returnObj
        

def CreateTiledMovieObject(filename, screenRect, pos, absRect, fullRect, loadAllMovieTiles=False, scale=None, allowFrameSkip=None):
    # A tiled movie object has a mostly frozen position on the display (for now)
    #   Each tile only loads the movie tiles that it will display at the 
    #   movie's current position.
    # Find the tiles that are located on the current display, load them, and
    #   position them.

    print "CreateTiledMovieObject"

    objectsToGroup = []

    # Load info from description
    des = ReadTiledMovieDescription(filename)
    tileFilenames = os.listdir(filename)
    print "tileFilenames:", tileFilenames

    # calculate adjustment in case full movie width and height are not 
    # evenly divisible by tile width and height.
    adjustment = (des["tileColsRows"][0] * des["tileRes"][0]-des["fullRes"][0],
                  des["tileColsRows"][1] * des["tileRes"][1]-des["fullRes"][1])

    imageBased = False
    if IsTiledMovieChunkImageBased(os.path.join(filename, tileFilenames[0])):
        imageBased = True

    for xIndex in range(des["tileColsRows"][0]):
        for yIndex in range(des["tileColsRows"][1]):     # TZ==TopZero
            yIndexBZ = des["tileColsRows"][1] - 1 - yIndex # BZ==BottomZero

            movieTileFilename = ""
            for f in tileFilenames:
                tileYIndex = yIndexBZ
                if imageBased:  # The 0th row for our movie and image loaders is different.
                    tileYIndex = yIndex
                if f.startswith("%s_%s." % (xIndex,tileYIndex)) or f == "%s_%s" % (xIndex,tileYIndex):
                    movieTileFilename = f
            fullMovieTilePath = os.path.join(filename, movieTileFilename)

            tileObject = None

            # full movie width and height are not evenly divisible by
            #   tile width and tile height, so adjust offset
            xSrcOffset = xIndex * des["tileRes"][0] - adjustment[0]
            ySrcOffset = yIndex * des["tileRes"][1] - adjustment[1]

            srcWidth,srcHeight = (des["tileRes"][0], des["tileRes"][1]) 


            # adjust a possibly small row or column's offset and size
            #   might only be necessary for y, since y is flipped (x untested).
            #if xIndex == 0:
            #    xOffset -= adjustment[0]
            #    width -= adjustment[0]


            if scale != None:
                xRenderOffset = xIndex * des["tileRes"][0] * scale[0] - adjustment[0] 
                yRenderOffset = yIndex * des["tileRes"][1] * scale[1] - adjustment[1] * scale[1]
                # remove the adjustment when yIndex == 0
                if yIndex == 0:
                    yRenderOffset = yIndex * des["tileRes"][1] * scale[1]
                    srcHeight -= adjustment[1] 
                renderWidth, renderHeight = srcWidth * scale[0], srcHeight * scale[1]
            else:
                # remove the adjustment when yIndex == 0
                if yIndex == 0: # FIXME, if we ever use imagebased (slow, movies
                            #  from image files, this may have to be adjusted
                            #  to use tileYIndex and maybe flip signs below.
                    ySrcOffset += adjustment[1]
                    srcHeight -= adjustment[1]
                xRenderOffset, yRenderOffset = xSrcOffset, ySrcOffset
                renderWidth, renderHeight = srcWidth, srcHeight

            #xSrcOffset = xIndex * des["tileRes"][0]
            #ySrcOffset = yIndex * des["tileRes"][1]

            #moviePos = Vec2(pos[0] + xSrcOffset, pos[1] + ySrcOffset)
            moviePos = Vec2(pos[0] + xRenderOffset, pos[1] + yRenderOffset)

            #movieRect = Rect(pos[0] + xSrcOffset, pos[1] + ySrcOffset, srcWidth, srcHeight)
            movieRenderRect = Rect(pos[0] + xRenderOffset, pos[1] + yRenderOffset, renderWidth, renderHeight)
            # print "Checking colliderects to see if movie tile is on this display tile:", movieRenderRect.colliderect(absRect), movieRenderRect, absRect, movieRenderRect.colliderect(absRect), "indexes:", xIndex, yIndex, "flipped indexes:", xIndex,yIndexBZ

            if loadAllMovieTiles or movieRenderRect.colliderect(absRect):
                movieTileFilename = ""
                for f in tileFilenames:
                    if f.startswith("%s_%s." % (xIndex,yIndexBZ)) or f == "%s_%s" % (xIndex,yIndexBZ):
                        movieTileFilename = f
                print "movieTileFilename:", movieTileFilename, len(movieTileFilename)
                if len(movieTileFilename.strip()) > 0:
                    print "movieTileFilename:", movieTileFilename, len(movieTileFilename)
                    print "TiledMovie: loading tile: ", fullMovieTilePath
                    # obj.pos and obj.size will be used to group movie tiles.
                    tileObject = CreateMovieObject(fullMovieTilePath, screenRect, moviePos, absRect, fullRect, fps=des["FPS"], scale=scale, allowFrameSkip=allowFrameSkip)
                else:
                   print "Warning movieTile not found for:", xIndex, yIndex

            if not tileObject:
                tileObject = NullTileDisplayObject(pos=moviePos,size=(movieRenderRect.width,movieRenderRect.height) ) # Empty object to represent
                                                     # objects on other nodes
                                                 # and keep object list synced.
            objectsToGroup.append(tileObject)

    shortName = os.path.basename(filename.strip(os.path.sep))
    groupObject = TiledMovieGroupObject(shortName, objectsToGroup, duration=des["duration"], fps=des["FPS"])

    groupObject.doChildUpdates=True
    returnObj = groupObject
    return returnObj

def CreateTileImageObject(imageFilename, screenRect, pos, absRect, fullRect, blend=True, scale=None):
    print "CreateTileImageObject", imageFilename, "at", pos
    imageSize = Image.open(imageFilename).size
    maxTextureSize = GetMaxTextureSize() 
    numTiles = ( int(math.ceil(float(imageSize[0]) / maxTextureSize)),
                 int(math.ceil(float(imageSize[1]) / maxTextureSize))  )
    print "NUMTILES:", numTiles

    if numTiles[0] == 1 and numTiles[1] == 1:
        returnObj = glTxtrBox(imageFilename, screenRect=screenRect, imagePos=pos, absRect= absRect, fullRect=fullRect, blend=blend, scale=scale)

    else:
        objectsToGroup = []

        # Create a group object
        xSrcOffset = 0
        xRenderOffset = 0
        subImageWidth = imageSize[0] / numTiles[0]
        subImageHeight = imageSize[1] / numTiles[1]
        for xIndex in range(numTiles[0]):
            ySrcOffset = 0
            yRenderOffset = 0

            if xIndex == numTiles[0] - 1:
                # make sure we don't cut off any
                # pixels if it's not evenly divisible.
                width = imageSize[0] - xSrcOffset
            else:
                width = subImageWidth

            for yIndex in range(numTiles[1]):

                if yIndex == numTiles[1] - 1:
                    # make sure we don't cut off any
                    # pixels if it's not evenly divisible.
                    height = imageSize[1] - ySrcOffset
                else:
                    height = subImageHeight

                pos = Vec2(xRenderOffset, -yRenderOffset)  # flip y coord
                # cropRect is for cropping a subsection out of the source image 
                cropRect = Rect(xSrcOffset, ySrcOffset, width, height)
                print "Loading with crop rect:", cropRect
                obj = glTxtrBox(imageFilename, screenRect=screenRect, imagePos=pos, absRect= absRect, fullRect=fullRect, blend=blend, cropRect=cropRect, scale=scale) 
                objectsToGroup.append(obj)

                ySrcOffset += obj.getSrcSize()[1]
                yRenderOffset += obj.getRenderSize()[1]
            xSrcOffset += obj.getSrcSize()[0]
            xRenderOffset += obj.getRenderSize()[0]

        shortName = os.path.basename(imageFilename.strip(os.path.sep))
        groupObject = GroupObject(shortName, objectsToGroup)
        returnObj = groupObject
    print "************* CreateTileDisplayObject finished", returnObj
    return returnObj

def CreateTileDisplayStreamObject(address, screenRect, pos, absRect, fullRect, blend=True, scale=None):
    #from streamView import StreamView, StartStreamViewLoop
    #streamView = StreamView()
    ##obj = CreateObj(None, imagePos=(0, 0), obj=streamView)
    ##objectsListList.append(obj)
    #StartStreamViewLoop(address)
    #return streamView

    #obj = glTxtrBox(imageFilename, screenRect=screenRect, imagePos=pos, absRect= absRect, fullRect=fullRect, blend=blend, cropRect=cropRect, scale=scale)
    streamObj = glStreamedTxtrBox(address, screenRect=screenRect, imagePos=pos, absRect= absRect, fullRect=fullRect, blend=blend, scale=scale)

    return streamObj

def CreateGroupTileDisplayStreamObject(address, objDesc, screenRect, pos, absRect, fullRect, blend=True, scale=None, gridColsRows=None):
    #from streamView import StreamView
    groupStreamObj = GroupTiledStreamObject(address, objDesc, screenRect=screenRect, pos=pos, absRect= absRect, fullRect=fullRect, blend=blend, scale=scale, gridColsRows=gridColsRows)

    return groupStreamObj

def CreateMultiNetGroupTileDisplayStreamObject(addresses, objDesc, screenRect, pos, absRect, fullRect, gridColsRows, netGridColsRows, blend=True, scale=None, doCenter=True, plant=False):
    #from streamView import StreamView
    objectsToGroup = []
    if len(addresses) != netGridColsRows[0] * netGridColsRows[1]:
        raise Exception("Number of addresses should match number of net grid tiles (e.g. use: --streamGroupsColsRows=3x2). currently: %d, %s" % (len(addresses), netGridColsRows) )
    #for address in addresses:

    gridCols = gridColsRows[0]
    gridRows = gridColsRows[1]
    bigTileWidth = gridCols * objDesc.streamWidth # 352
    bigTileHeight = gridRows * objDesc.streamHeight # 288
    if scale != None:
        bigTileWidth *= scale[0]
        bigTileHeight *= scale[1]
    netGridCols = netGridColsRows[0]
    netGridRows = netGridColsRows[1]
    print "BIGTILESIZE:", bigTileWidth, bigTileHeight

    basePos = pos
    if doCenter:
        centeredPos = Vec2(pos[0], pos[1]) - Vec2(netGridCols * bigTileWidth/2, netGridRows * bigTileHeight/2)
        basePos = centeredPos
    
    # for xcol in range(1,2): 
    print "grid within network stream:", gridCols, gridRows
    print "bigTile width,height:", bigTileWidth, bigTileHeight
    for xcol in range(netGridCols):
        for yrow in range(netGridRows):
            streamAddressIndex = netGridCols * yrow + xcol  # btm left to right, to top
            address = addresses[streamAddressIndex]
            yOffset = yrow * bigTileHeight
            xOffset = xcol * bigTileWidth
            singlePos = Vec2(xOffset+basePos[0],yOffset+basePos[1]) 

            loadTile = True
            if plant:  # only load if it's on this machine
                streamTileRenderRect = Rect(singlePos[0], singlePos[1], bigTileWidth, bigTileHeight)
                # print "Checking colliderects to see if stream tile is on this display tile:", movieRenderRect.colliderect(absRect), movieRenderRect, absRect, movieRenderRect.colliderect(absRect), "indexes:", xIndex, yIndex, "flipped indexes:", xIndex,yIndexBZ
                if streamTileRenderRect.colliderect(absRect):
                    loadTile = True
                    # Debug
                    import mpi 
                    print mpi.rank, " Loading stream with rect: ", streamTileRenderRect, "me:", (absRect.x,absRect.y,absRect.width,absRect.height), address
                else:
                    import mpi 
                    print mpi.rank, " Not loading stream with rect: ", streamTileRenderRect, "me:", (absRect.x,absRect.y,absRect.width,absRect.height), address
                    loadTile = False

            if loadTile:
                groupStreamObj = GroupTiledStreamObject(address, objDesc, screenRect=screenRect, pos=singlePos, absRect= absRect, fullRect=fullRect, blend=blend, scale=scale, gridColsRows=gridColsRows, doCenter=False)
                objectsToGroup.append(groupStreamObj)
            else:
                groupStreamObj = NullTileDisplayObject(pos=singlePos,size=(bigTileWidth,bigTileHeight) ) # Empty object to represent objects on other nodes and help describe large object on this node .
                objectsToGroup.append(groupStreamObj)
     
    shortName = "_".join(addresses)
    largeGroupObject = GroupObject(shortName, objectsToGroup, doChildUpdates=True)

    return largeGroupObject



def CreateTileDisplayObject(imageFilename, screenRect, pos, absRect, fullRect, blend=True, loadAllMovieTiles=False, scale=None, allowFrameSkip=None):

    print "************* CreateTileDisplayObject"

    if IsMovieFile(imageFilename):
        print "CREATE MOVIE:", pos
        movieObj = CreateMovieObject(imageFilename, screenRect, pos, absRect, fullRect, scale=scale, allowFrameSkip=allowFrameSkip)
        print "************* CreateTileDisplayObject finished", movieObj
        return movieObj

    if IsTiledMoviePath(imageFilename):
        print "CREATE TILED MOVIE:", pos
        movieObj = CreateTiledMovieObject(imageFilename, screenRect, pos, absRect, fullRect, loadAllMovieTiles=loadAllMovieTiles, scale=scale, allowFrameSkip=allowFrameSkip)
        print "************* CreateTileDisplayObject finished", movieObj
        return movieObj

    else:
        return CreateTileImageObject(imageFilename, screenRect, pos, absRect, fullRect, scale=scale)

    

