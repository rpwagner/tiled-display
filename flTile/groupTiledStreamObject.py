import os
from baseTileDisplayObject import BaseTileDisplayObject, NullTileDisplayObject
from glUtils import glStreamedTxtrBox
from flapp.pmath.vec2 import Vec2
from flapp.pmath.rect import Rect

try:
    from streamView import StreamState
except Exception, e:
    print "streamView.py not found in flTile.  Put it in flTile to enable streaming."
    GroupTiledStreamObject = None

class GroupTiledStreamObject(BaseTileDisplayObject):
    def __init__(self, address, objDesc, screenRect, fullRect, absRect, zoom=(4,4), pos=None, size=None, blend=False, cropRect=None, fps=None, scale=None, allowFrameSkip=True, gridColsRows=None, doCenter=True):
        BaseTileDisplayObject.__init__(self, screenRect=screenRect, fullRect=fullRect, absRect=absRect, zoom=zoom, pos=pos, size=size, blend=blend, cropRect=cropRect)
        self.address = address
        if gridColsRows == None:
            self.streamCols = 1
            self.streamRows = 1
        else:
            self.streamCols = gridColsRows[0]
            self.streamRows = gridColsRows[1]
        #self.streamWidth = 352
        #self.streamHeight = 288
        self.streamWidth = objDesc.streamWidth
        self.streamHeight = objDesc.streamHeight
        if scale != None:
            self.streamWidth *= scale[0]
            self.streamHeight *= scale[1]
        addVisibleSeparation = False
        if addVisibleSeparation:
            self.streamWidth += 3
            self.streamHeight += 3
        self.size = self.streamCols * self.streamWidth, self.streamRows * self.streamHeight
        self.streamObjs = []

        # print "GROUP:", self.pos, self.size
        if doCenter:
            # center on pos
            self.setPos(pos[0] -self.size[0]/2, pos[1] - self.size[1]/2)


        for r in range(self.streamRows):
            for c in range(self.streamCols):
                objOffset = Vec2(c * self.streamWidth, r * self.streamHeight)
                #objPos = (self.pos[0] + c * self.streamWidth, self.pos[1] + r * self.streamHeight)
                objPos = Vec2(self.pos[0] + objOffset[0], self.pos[1] + objOffset[1])
                streamObj = glStreamedTxtrBox(address, screenRect=screenRect, imagePos=objPos, absRect= absRect, fullRect=fullRect, blend=blend, scale=scale, streamState=StreamState(), streamWidth=objDesc.streamWidth, streamHeight=objDesc.streamHeight, vflip=objDesc.vflip)
                streamObj.groupOffset = objOffset
                self.streamObjs.append(streamObj)

        # information for sorting and aligning tiles
        self.targetLocationOrder = []
        self.locations = []
        for r in range(self.streamRows):
            for c in range(self.streamCols):
                self.locations.append(Vec2(c * self.streamWidth, r * self.streamHeight))
                #nC = self.streamCols-c
                #self.targetLocationOrder.append(r*self.streamCols+c)
        self.initialObjOrder = list(self.streamObjs)

        # DEBUG
        #self.targetLocationOrder = [ 0, 1, 2, 3]  # numbers for the location
        self.targetLocationOrder = range(self.streamRows*self.streamCols)

    def setPos(self, x, y):
        BaseTileDisplayObject.setPos(self, x,y)
        for streamObj in self.streamObjs:
            streamObj.setPos(*(self.pos + streamObj.groupOffset))

    def reorder(self, indexNamesDict):
        #print "reordering with names:", indexNamesDict.values(), indexNamesDict.keys(), self.address
        # print "mypos:", self.getPos(), self.address
        # reverse so we can sort by name and keep the index
        namesIndexList = [ (name,index) for index,name in indexNamesDict.items() ]
        # namesIndexList.sort()
        # print "Sorted:", namesIndexList

        for i in range(len(namesIndexList)):
            name, index = namesIndexList[i]
            if not name.startswith("ABC"):
                continue   # avoid extra or unnamed streams
            obj = self.initialObjOrder[index]
            #locationIndex = self.targetLocationOrder[i]  # this works, but not if there are
                                                          # extra or old streams

            locationIndex = self.targetLocationOrder[int(name[6:8])] # Use 

            offsetLocation = self.locations[locationIndex]
            obj.groupOffset = offsetLocation
            obj.setPos( *(self.pos + offsetLocation) )
            """
            if name and name.startswith("ABCViz00"):
                obj.setPos( *self.pos )
            elif name and name.startswith("ABCViz01"):
                obj.setPos( *self.pos + Vec2(self.streamWidth, 0) )
            elif name and name.startswith("ABCViz02"):
                obj.setPos( *self.pos + Vec2(0, self.streamHeight) )
            elif name and name.startswith("ABCViz03"):
                obj.setPos( *self.pos + Vec2(self.streamWidth, self.streamHeight) )
            else:
                obj.setPos( 1000,1000 )
            """


    

    def setStreamState(self, streamStateList):
        for i in range(len(streamStateList)):
            self.streamObjs[i].setStreamState(streamStateList[i])

    def getNumStreams(self):
        return self.streamRows * self.streamCols

    def draw(self, renderer):
        for o in self.streamObjs:
            o.draw(renderer)

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
        for o in self.streamObjs:
            o.update(secs, app)

    def isPixelTransparent(self, (x,y) ):
        return False

    def getRect(self):
        return Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

    def getWidth(self):
        return self.size[0]

    def getHeight(self):
        return self.size[1]

