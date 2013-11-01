from flTileMpi import mpi

def findFirstObjAt(objects, (x, y), renderers ):
    # Use the order from the renderer
    tmpObjs = []
    renderOrder = list(renderers[0].getRenderOrder())
    renderOrder.reverse() 
    #for i in range(len(renderers[0].objects)-1, -1, -1): # reverse order
    #    if i+1 < len(renderers[0].objects):
    #        if renderers[0].objects[i+1] in objects:
    #            tmpObjs.append(renderers[0].objects[i+1])
    for i in renderOrder:
        robj = renderers[0].getObjectById(i)
        if robj != None and robj in objects:
            if "group" in dir(robj) and robj.group is not None:
                if robj.group not in tmpObjs:
                    tmpObjs.append(robj)
            else:
                tmpObjs.append(robj)
    #print "Comparing object lists:", objects, renderers[0].objects
    #for obj in objects:
    for obj in tmpObjs:
        p = obj.getPos()
        tr = p[0] + obj.getSize()[0], p[1] + obj.getSize()[1]
        if x >= p[0] and y >= p[1] and x <= tr[0] and y <= tr[1]:
            imagecoords = x - p[0], y - p[1]
            if not obj.isPixelTransparent( imagecoords ):
                return obj
    return None

class TileDeviceController:
    # FIXME finish updating to use visualsManager isntead of renderes, cursorListList, etc.
    def __init__(self, tileMousePos, inputManager=None, configUI=None, renderers=None, masterObjects=None, cursorListList=None):
        self.inputManager=inputManager # the manager/holder of the devices
        self.tileMousePos = tileMousePos
        self.target = None
        self.focusObj = None # like target, but persists after mouse up
        self.renderers = renderers
        self.configUI = configUI
        self.masterObjects=masterObjects
        if cursorListList == None:
            self.cursorListList=[]
        else:
            self.cursorListList=cursorListList

    def selectTarget(self, target):
        self.target=target
        self.focusObj=target
        if (self.target != None):
            pos = self.tileMousePos.getDisplayPos()
            pos2 = self.target.getPos()
            self.targetOffset = pos[0] - pos2[0], pos[1] - pos2[1]
            # self.renderers[0].sendObjToBack(self.target)
            self.renderers[0].bringObjToFront(self.target)
            for cursorList in self.cursorListList:
                self.renderers[0].bringObjToFront(cursorList[0])
            for renderer in self.renderers[1:]:
                renderer.setRenderOrder(self.renderers[0].getRenderOrder())
        # self.target = self.masterObjects[0]

    def deselectTarget(self):
        self.target=None
        # self.focusObj keeps the value, even after mouse has let up

    def rightClickDown(self):
        target = findFirstObjAt(self.masterObjects, self.tileMousePos.getDisplayPos(), renderers=self.renderers)
        if target != None:
            pos = self.tileMousePos.getDisplayPos()
            pos2 = target.getPos()
            self.targetOffset = pos[0] - pos2[0], pos[1] - pos2[1]
            self.renderers[0].sendObjToBack(target)
            for renderer in self.renderers[1:]:
                renderer.setRenderOrder(self.renderers[0].getRenderOrder())

    def leftClickDown(self):
        #print "LEFTCLICKDOWN"
        target = findFirstObjAt(self.masterObjects, self.tileMousePos.getDisplayPos(), renderers=self.renderers)
        self.selectTarget(target)
        """
        if (self.target != None):
            pos = self.tileMousePos.getDisplayPos()
            pos2 = self.target.getPos()
            self.targetOffset = pos[0] - pos2[0], pos[1] - pos2[1]
            self.renderers[0].sendObjToBack(self.target)
            #for cursorList in self.cursorListList:
            #    self.renderers[0].bringObjToFront(cursorList[0])
            for renderer in self.renderers[1:]:
                renderer.setRenderOrder(self.renderers[0].getRenderOrder())
        # self.target = self.masterObjects[0]
        """

    def leftClickUp(self):
        #print "LEFTCLICKUP"
        # self.target = None
        self.deselectTarget()

    def setMousePosNormalized(self, x, y):
        self.tileMousePos.setMousePosNormalized(x,y)
        self.updateTargetPos()

    def mouseButtonDownEvent(self, x, y, buttonId):
        print "mousebuttondown", buttonId
        self.tileMousePos.setMousePosNormalized(x,y)
        if 0 == buttonId:
            self.leftClickDown()
        elif 2 == buttonId:
            self.rightClickDown()
        elif 3 == buttonId:
            self.mouseScrollUp()
        elif 4 == buttonId:
            self.mouseScrollDown()
        #elif 0 == buttonId:
        #    self.leftClickUp()
        self.updateTargetPos()

    def mouseButtonUpEvent(self, x, y, buttonId):
        print "mousebuttonup", buttonId
        self.tileMousePos.setMousePosNormalized(x,y)
        self.updateTargetPos()
        self.deselectTarget()

    def update(self, secs, app):
        pass # might add things later

    def updateTargetPos(self):
        if self.target != None:
            #print "TARGET:", self.target, self.target.__class__, self.target.__class__.__name__
            # FIXME, tmp, change to more general check
            if self.target.__class__.__name__ != "TiledMovieGroupObject":
                pos = self.tileMousePos.getDisplayPos()
                #print "Target orig pos:", self.target.getPos()
                self.target.setPos(pos[0] - self.targetOffset[0], pos[1] - self.targetOffset[1])
                #print "Updated target to pos:", pos, (pos[0] - self.targetOffset[0], pos[1] - self.targetOffset[1]), self.target.getPos()

    def scaleFocusObj(self, increment, scaleCenterAtCursor=False):
        #  Call setScale() on object
        #    then adjust it's position so it appears to be scaled from center (or cursor).
        
        if self.focusObj != None and self.focusObj.__class__.__name__ != "TiledMovieGroupObject":
            curScale = self.focusObj.getScale()
            origSize = self.focusObj.getSize()
            if curScale:
                self.focusObj.setScale( (curScale[0]+increment, curScale[1]+increment) )
            else:
                self.focusObj.setScale( (1.0+increment, 1.0+increment))
            newSize=self.focusObj.getSize()
            curPos = self.focusObj.getPos()
            sizeDiff = ((newSize[0]-origSize[0]), (newSize[1]-origSize[1]) )
            if scaleCenterAtCursor: # had suggestion to scale with center at the cursor position:
                percent = ( (self.tileMousePos.getDisplayPos()[0] - curPos[0]) / (origSize[0] ), 
                            (self.tileMousePos.getDisplayPos()[1] - curPos[1]) / (origSize[1] ) )
                offset = sizeDiff[0]*(1.0-percent[0]), sizeDiff[1]*(1.0-percent[1])
            else:
                offset = sizeDiff[0]/2, sizeDiff[1]/2
            self.focusObj.setPos( curPos[0] - offset[0], curPos[1] - offset[1])

    def keyDownEvent(self, key, x, y):
        print "keydown key:", key, x, y
        if key == "+" or key == "=":
            self.scaleFocusObj(0.05, scaleCenterAtCursor=False)
        elif key == "-":
            self.scaleFocusObj(-0.05, scaleCenterAtCursor=False)
        elif key == "r": # reset scale
            if self.focusObj != None and self.focusObj.__class__.__name__ != "TiledMovieGroupObject":
                # also reposition so object's center is stationary 
                origSize = self.focusObj.getSize()
                curPos = self.focusObj.getPos()

                self.focusObj.setScale( (1.0, 1.0) )

                newSize=self.focusObj.getSize()
                sizeDiff = ((newSize[0]-origSize[0]), (newSize[1]-origSize[1]) )
                offset = sizeDiff[0]/2, sizeDiff[1]/2

                self.focusObj.setPos( curPos[0] - offset[0], curPos[1] - offset[1])
        else:
            print "unhandled keydown:", key

    def mouseScrollDown(self):
        self.scaleFocusObj(0.02, scaleCenterAtCursor=True)

    def mouseScrollUp(self):
        self.scaleFocusObj(-0.02, scaleCenterAtCursor=True)

    def stringEvent(self, arg):
        arg = arg.lower().strip()
        # for now, process simple strings, later we'll process args
        if self.focusObj != None:
            if self.focusObj.__class__.__name__ == "TiledMovieGroupObject":
                print arg
                if arg == "pause":
                    self.focusObj.pause()
                elif arg == "togglepause":
                    self.focusObj.togglePause()
                elif arg == "skipback":
                    print "skipback disabled for now -- movies are setup to continue for smoothness"
                    #self.focusObj.skipBack(8)
                elif arg == "skipforward":
                    print "skipfwd disabled for now -- movies are setup to continue for smoothness"
                    #self.focusObj.skipForward(8)
                else:
                    print "TileDeviceController::stringEvent, tiledmovieobj, unhandled:", arg
            else:
                    print "TileDeviceController::stringEvent, not a tiledmovieobj, unhandled:", arg
                    print "obj is:", self.focusObj

        if arg.lower() == "quit":
            print "\"quit\" message received."
            if self.inputManager:
                #self.inputManager.app.quit()
                #self.inputManager.app.callLater(0.0, self.inputManager.app.quit, [])
                self.inputManager.app.state.setFlagToExit()
            else:
                print "Not stopping app, device has no inputManager"
        else:
            print "TileDeviceController::stringEvent, no obj selected, unhandled:", arg


class WiiMouseUpdater(TileDeviceController):
    def __init__(self, moteMouse, tileMousePos, inputManager=None, configUI=None, renderers=None, masterObjects=None, cursorListList=None, moteManager=None):
        TileDeviceController.__init__(tileMousePos, inputManager, configUI, renderers, masterObjects, cursorListList, moteManager)
        self.moteMouse = mouseMouse
        self.moteManager=moteManager

    def update(self, secs, app):
        TileDeviceController.update(secs, app)

        # process data from device
        if mpi.rank == 0 and self.moteMouse.mote != None:
            self.moteMouse.processAndUpdateMouse()
            buttonEvents = self.moteMouse.mote.extractButtonEvents()
            for event in buttonEvents:
                self.processEvent(event)

            if self.target != None:
                pos = self.tileMousePos.getDisplayPos()
                #self.target.setPos(pos[0] - self.targetOffset[0], pos[1] - self.targetOffset[1])
                self.updateTargetPos(*pos)

    def processEvent(self, event):
        print "BUTTON:", event[0],
        if event[1]:
            print "pressed."
        else:
            print "released."
        if event[0] == "h":
            if event[1] == True:
                # self.configUI.toggleOnOff()
                print "(h) pressed, Note: ConfigUI toggle not in use"    
        elif self.configUI and self.configUI.enabled:
            self.configUI.buttonEvent(event)
        elif event[0] == "a":
            #print "A PRESSED"
            if event[1] == True:
                self.target = findFirstObjAt(self.masterObjects, self.tileMousePos.getDisplayPos(), renderers=self.renderers)
                if (self.target != None):
                    pos = self.tileMousePos.getDisplayPos()
                    pos2 = self.target.getPos()
                    self.targetOffset = pos[0] - pos2[0], pos[1] - pos2[1]
                    self.renderers[0].bringObjToFront(self.target)
                    for cursorList in self.cursorListList:
                        self.renderers[0].bringObjToFront(cursorList[0])
                    for renderer in self.renderers[1:]:
                        renderer.setRenderOrder(self.renderers[0].getRenderOrder())
                # self.target = self.masterObjects[0]
            else:
                self.target = None
        elif event[0] == 1:
            if event[1] == True:
                self.leftClickDown()
            else:
                self.leftClickUp()
                # self.target = None
        elif event[0] == "m" and event[1] == True: # "-" button down
            print "- pressed, disconnecting"
            #print event
            if self.moteManager:
                self.moteManager.disconnectMote(self.moteMouse.mote.id)
                print "Mote Timeout, Will start searching in 5 sec (to avoid auto-reconnect)"
                app.callLater(5.0, self.moteManager.moteDetector.reinitiateSearching, [])
        elif event[0] == "p" and event[1] == True:   # "+" button down
            self.moteManager.incrementNumMotes(1)


