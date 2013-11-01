from flapp.pmath.vec2 import Vec2
from flapp.pmath.rect import Rect
from glUtils import glTxtrBox
import copy
import traceback

class BaseObject:
    # other things don't need to inherit this, but
    #   need to have similar functions.
    def __init__(self):
        self.pos = Vec2(0.0,0.0)

    def setPos(self, x, y):
        self.pos = Vec2(x,y)

    def getPos(self):
        return self.pos


class GroupObject(BaseObject):
    def __init__(self, name, objectsToGroup=None, doChildUpdates=False):
        BaseObject.__init__(self)
        self.name = name
        self.childrenAndOffsets = {}
        if objectsToGroup:
            for o in objectsToGroup:
                print "ADDING Group obj:", o.getRect(), o # , self.getPos()
                self.childrenAndOffsets[o] = o.getPos() - self.getPos()
                o.group = self
        self.resetPosFromChildren()
        self.doChildUpdates = doChildUpdates
        self.hidden = False

    def getScale(self):
        return self.childrenAndOffsets.keys()[0].getScale()

    def setScale(self, (x,y)):
        for o in self.childrenAndOffsets.keys():
            o.setScale( (x,y) )

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def isHidden(self):
        return self.hidden

    def getChildren(self):
        return self.childrenAndOffsets.keys()

    def resetPosFromChildren(self):
        rect = self.getChildrenRect() # the rect origin is the new group origin
        if rect:
            difference = Vec2(rect.x, rect.y) - self.getPos()
            for child, offset in self.childrenAndOffsets.items(): 
                self.childrenAndOffsets[child] = offset - difference
        self.setPos(rect.x, rect.y)
        print "Group Object pos (after reset pos from children:", self.getPos()

    def addObject(o, offset=None):
        if offset == None:
            currentPos = o.getPos()
            self.children[o] = Vec2(currentPos[0], currentPos[1])
        else:
            self.children[o] = Vec2(offset[0], offset[1])
        o.group = self
        self.resetPosFromChildren()

    def update(self, secs, app):
        try:
            if self.doChildUpdates:
                for child, offset in self.childrenAndOffsets.items():
                    child.update(secs, app)

            for child, offset in self.childrenAndOffsets.items():
                child.setPos( *(self.getPos() + offset) )

        except:
             traceback.print_exc()

    def draw(self, renderer):
        if not self.hidden:
            try:
                for child in self.childrenAndOffsets:
                    child.draw(renderer)
            except:
                 traceback.print_exc()

    def getChildrenRect(self):
        if len(self.childrenAndOffsets) == 0:
            return Rect(0,0, 0, 0)

        # union all child rects and report size
        children = self.childrenAndOffsets.keys()
        rect = copy.copy(children[0].getRect())
        for child in children[1:]:
            # print "   child rect:", child.getRect()
            if child.getRect(): # avoid None
                if rect:        #avoid None
                    rect = rect.union(child.getRect())
                else:
                    rect = copy.copy(child.getRect())
                    
        print "GET CHILDREN RECT:", rect
        return rect

    def getSize(self):
        rect = self.getChildrenRect()
        return Vec2(rect.width, rect.height)

    def getWidth(self):
        return self.getSize()[0]

    def getHeight(self):
        return self.getSize()[1]

    def isPixelTransparent(self, imagecoords):
        for child,offset in self.childrenAndOffsets.items():
            # need to adjust image coords to match individual image instead of group rect
            #print "orig imagecoords:", imagecoords
            #print "child coords:", child.getPos(), "group coords:", self.getPos()
            offset = child.getPos() - self.getPos()
            tileImagecoords =  Vec2(imagecoords[0] - offset.x, imagecoords[1] - offset.y)
            #print "modified imagecoords:", tileImagecoords
            if ( Rect(0,0,child.getWidth(), child.getHeight()).containsPoint(*tileImagecoords) and
                not child.isPixelTransparent(tileImagecoords) ):
                return False
        return True
       

