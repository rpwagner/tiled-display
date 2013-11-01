from flTileMpi import mpi

from threading import Lock
import traceback
import time

class GenericSyncer:
# broadcasts data from the master node to all other nodes.
    def __init__(self, data=None, updateCallback=None, dataSources=None, reportFramerate = True):
        # data sources should have the function storeDataInDict(dict)
        # list of objects to sync to list of positions:  [ [a1,a2,a3], [b1,b2] ]
        #
        self.data = data
        self.resultData = None

        self.dataSources = dataSources
        if self.dataSources == None:
            self.dataSources = []

        self.updateCallback=updateCallback

        #if mpi.rank == 0:
        #    self.dataLock = Lock()
        self.reportFramerate = reportFramerate
        self.lastTime = time.time()
        self.reportInterval = 2.0
        self.frameCount = 0

    def update(self, secs, app):
        self.syncAndApply()

        if mpi.rank == 0 and True == self.reportFramerate:
            self.frameCount += 1
            self.updateFramerateReport()

    def updateFramerateReport(self):
        if (time.time() - self.lastTime) > self.reportInterval:
            print "FPS:",  self.frameCount / (time.time() - self.lastTime)
            self.lastTime = time.time()
            self.frameCount = 0


    def syncAndApply(self):
        # Get updated data from data sources
        for obj in self.dataSources:
            obj.storeDataInDict(self.data)


        # could lock the data and make a copy before sending, but this is
        #   good enough for now

        if mpi.rank == 0:
            self.resultData = mpi.bcast(self.data)
        else:
            self.resultData = mpi.bcast()
            #if len(self.data) > 0:
                #if mpi.rank == 1:
                #    print "Received data:", self.resultData

        if self.updateCallback != None:
            self.updateCallback(self.resultData)

    def getSyncExampleDict(self):
        for obj in self.dataSources:
            obj.storeDataInDict(self.data)
        return dict(self.data)

class Syncer:
    # An older version of the more general syncer above.
    #  The "cursors" that are synced are any graphical object whose
    #     position needs to be synced across nodes.
    def __init__(self, cursorObjectsListList=None, dataObjList=None):
        # list of objects to sync to list of positions:  [ [a1,a2,a3], [b1,b2] ]
        #  
        # access: cursor[i][localcopies]
        # only the first object for each cursors is read, all are written
        if cursorObjectsListList == None:
            self.cursorObjects = []
        else:
            self.cursorObjects = cursorObjectsListList

        if dataObjList == None:
            self.dataObjList = []
        else:
            self.dataObjList = dataObjList

        self.data = []
        for obj in self.dataObjList:
            self.data.append([])

        self.cursors = []
        for obj in self.cursorObjects:
            self.cursors.append( (0,0) )

        self.resultCursors = []
        if mpi.rank == 0:
            self.dataLock = Lock()

    def addDataObj(self, obj): # should be done on all nodes at once
        self.dataObjList.append(obj)
        self.data.append([])

    def update(self, secs, app):
        mpi.barrier()
        self.syncAndApply()

    def syncAndApply(self):
        if mpi.rank == 0:
            self.dataLock.acquire() # this lock probably isn't necessary yet

            try:
                for i in range(len(self.cursorObjects)):
                    #self.cursors[i] = self.cursorObjects[i][0].getPos()
                    self.cursors[i] = (self.cursorObjects[i][0].getPos(), self.cursorObjects[i][0].getScale() or (1.0,1.0) )
                for i in range(len(self.dataObjList)):
                    self.data[i] = self.dataObjList[i].getData()
                    # print "Sending data:", self.data
                #print "syncing %s cursors and %s data." % (len(self.cursorObjects), len(self.dataObjList)), self.dataObjList[0]

            except:
                traceback.print_exc()
            finally:
                self.dataLock.release()

        if mpi.rank == 0:
            self.resultCursors = mpi.bcast(self.cursors)
            if len(self.data) > 0:
                self.resultData = mpi.bcast(self.data)
        else:
            self.resultCursors = mpi.bcast()
            if len(self.data) > 0:
                self.resultData = mpi.bcast()
                #if mpi.rank == 1: 
                #    print "Received data:", self.resultData

        if mpi.rank != -1: #ok, done for all
            for i in range(len(self.cursorObjects)):
                if len(self.resultCursors) > i:
                    # access: cursorObjects[i][localcopies]
                    for j in range(len(self.cursorObjects[i])): # set for each local copy
                        # print "Obj data:", self.resultCursors[i]
                        self.cursorObjects[i][j].setPos( self.resultCursors[i][0][0], self.resultCursors[i][0][1])
                        self.cursorObjects[i][j].setScale( (self.resultCursors[i][1][0], self.resultCursors[i][1][1]) )
        if mpi.rank != 0:
            for i in range(len(self.dataObjList)):
               if len(self.resultData) > i:
                   self.dataObjList[i].setData(self.resultData[i])
            

        #if len(resultQueue) > 0:
        #    print "Bcasting recv:", resultQueue, mpi.rank
