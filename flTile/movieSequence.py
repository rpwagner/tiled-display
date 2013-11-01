
class MovieSequence:
    def __init__(self):
       self.objList = [] 
       self.activeObj = None
       self.activeObjIndex = 0
       self.objLoops = [] 
       self.currentObjPlayedLoops=0

    def update(self, secs, app):
        # print "MS update:", self.activeObj
        if None != self.activeObj:
            for activeObj in self.activeObj: # it's a list
                if activeObj.hasFinished():
                    # See if we should loop this movie or start the next
                    self.currentObjPlayedLoops += 1
                    startingAnotherLoop = False
                    if self.activeObjIndex < len(self.objLoops):
                        numLoopsToMake = self.objLoops[self.activeObjIndex]
                        if self.currentObjPlayedLoops < numLoopsToMake:
                            print "Starting another loop"
                            activeObj.rewind()
                            startingAnotherLoop = True
                    if not startingAnotherLoop:
                        self.gotoNext()

    def append(self, objList, loopsPerPlay=1):
        print "MOVIESEQ APPENDING OBJ:", objList
        for obj in objList:
            obj.setLoopOnFinish(False)
            obj.stop()
            obj.hide()
        self.objList.append(objList)
        self.objLoops.append(loopsPerPlay)

    def _initialize(self):
        if len(self.objList) > 0:
            self.activeObj = self.objList[0]
            self.activeObjIndex = 0

    def gotoNext(self):
        self.currentObjPlayedLoops=0
        if len(self.objList) > 0:
            if None == self.activeObj:
                self._initialize()
            else:
                # stop current obj
                for activeObj in self.activeObj:
                    activeObj.stop()
                    activeObj.hide()
                    activeObj.rewind()

                # update to next obj
                print "old index:", self.activeObjIndex
                self.activeObjIndex = (self.activeObjIndex + 1) % len(self.objList)
                self.verifyActiveObjIndex()
                self.activeObj = self.objList[self.activeObjIndex]
                print "new index:", self.activeObjIndex, len(self.objList)

                # start this next obj
                for activeObj in self.activeObj:
                    print "MOVIESEQ calling REWIND ****"
                    activeObj.rewind()
                    activeObj.start()
                    activeObj.show()
                    # self.activeObj.show()

    def storeDataInDict(self, dataDict):
        dataDict["activeIndex"]=self.activeObjIndex

    def setDataFromDict(self, data):
        if self.activeObjIndex != data["activeIndex"]:
            self.activeObjIndex = data["activeIndex"]
            try:
                self.activeObj = self.objList[self.activeObjIndex]
            except IndexError:
                print "WARNING: MovieSequence::setDataFromDict, activeObjIndex out of range"
                self.activeObjIndex = 0

    def verifyActiveObjIndex(self):
        if self.activeObjIndex >= len(self.objList):
            self.activeObjIndex = 0

    def initializeObjects(self):
        # make sure one obj is marked as active
        if None == self.activeObj and len(self.objList) > 0:
            self.verifyActiveObjIndex()
            self.activeObj = self.objList[self.activeObjIndex]

        for activeObj in self.activeObj:
            activeObj.rewind()
            activeObj.start()
            activeObj.show()

        """ # Done when first added now
        for obj in self.objList:  # stop and hide all objs except active one
            if obj != self.activeObj:
                obj.stop()
                obj.hide()
        """


