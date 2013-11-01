
# Mainly an XY (mouse) position 
#  An adapter for turning raw input data
#   into a useable screen/display position.
#   Can filter data (helpful for wiimote data)

class TileMote:
    def __init__(self, cursorObject, displayWidth, displayHeight, numToFilter=10 ):
        self.cursorObject = cursorObject
        self.lastX = 0
        self.lastY = 0
        self.queue = []
        #if mpi.rank == 0:
        #    self.dataLock = Lock()
        self.width = displayWidth
        self.height = displayHeight
        self.lastN = []
        self.numToFilter = numToFilter
        for i in range(numToFilter):
            self.lastN.append( (0,0) )
        self.useFilter = True
        self.filteredX = 0
        self.filteredY = 0

    def getDisplayPos(self):
        if self.useFilter:
            return (int(self.filteredX*self.width) ,int((1.0-self.filteredY)*self.height)) 
        else:
            return (int(self.lastX*self.width) ,int((1.0-self.lastY)*self.height)) 

    def getPos(self):
        if self.useFilter:
            return self.filteredX, self.filteredY
        else:
            return self.lastX, self.lastY

    def setMousePosNormalized(self, x, y):
        #print "Tile Mote queuing: ", x, y
        #self.dataLock.acquire() # this lock probably isn't necessary
        self.lastX = x
        self.lastY = y
        self.lastN.pop()            # get rid of old point
        self.lastN.insert(0, (x,y)) # add new point
        if self.useFilter:
            """
            sumX = 0
            sumY = 0
            for ix, iy in self.lastN:
                sumX += ix
                sumY += iy
            self.filteredX = sumX / self.numToFilter
            self.filteredY = sumY / self.numToFilter
            """
            #self.filteredX = (self.lastN[0][0] + 2.0 * self.filteredX) / 3
            #self.filteredY = (self.lastN[0][1] + 2.0 * self.filteredY) / 3
            self.filteredX = (self.lastN[0][0] + 3.0 * self.filteredX) / 4
            self.filteredY = (self.lastN[0][1] + 3.0 * self.filteredY) / 4
            self.cursorObject.setPos(int(self.filteredX*self.width) ,int((1.0-self.filteredY)*self.height)-self.cursorObject.getSize()[1]) 
        else:
            self.cursorObject.setPos(int(x*self.width) ,int((1.0-y)*self.height)) 
        #self.dataLock.release()

TileMousePosition = TileMote

