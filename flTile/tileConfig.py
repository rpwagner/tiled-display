import os, shutil
import traceback
from GUID import GUID

from flapp.pmath.rect import Rect

class TileDesc:
    def __init__(self, pixelSize, localOffset=(0,0), displayStr=":0", lrtbBorders=(0,0,0,0) , lrtbMullions=(0,0,0,0), uid=None, location=None, localWindowId=0):
        # local rect should have attributes x, y, width, and height

        if uid == None:
            self.uid = GUID()
        else:
            self.uid = uid
        
        # border is often an overlap and is usually left black.
        # mullions are adjusted to 
        # self.pixelSize = width, height
        self.pixelSize = pixelSize
        self.localOffset = localOffset
        self.displayStr = displayStr
        self.borders = list(lrtbBorders)
        self.mullions = list(lrtbMullions) 

        if location == None:
            self.location = TileLocation( (0,0), relative=False)
        else:
            self.location = location

        self.localWindowId=localWindowId

    def setMullion(self, lrtb):
        self.mullions = lrtb

    def getMullion(self):
        return self.mullions

    def modifyMullion(self, lrtb):
        self.mullions = (lrtb[0] + self.mullions[0],
                         lrtb[1] + self.mullions[1],
                         lrtb[2] + self.mullions[2],
                         lrtb[3] + self.mullions[3])

    def __eq__(self, otherMachine):
        if (self.uid == otherMachine.uid and
            self.pixelSize == otherMachine.pixelSize and
            self.localOffset == otherMachine.localOffset and
            self.borders == otherMachine.borders and
            self.mullions == otherMachine.mullions and
            self.location == otherMachine.location and
            self.displayStr == otherMachine.displayStr):
            return True
        else:
            return False

    def asDict(self):
        if self.location != None:
            locationDict = self.location.asDict()
        else:
            locationDict = None
        d = {"uid": self.uid,
             "pixelSize": self.pixelSize,
             "localOffset": self.localOffset,
             "displayStr": self.displayStr,
             "borders": self.borders,
             "mullions": self.mullions,
             "location": locationDict
        }
        return d

    def getDrawSize(self):
        return (width - rightBorder - leftBorder,
                height - topBorder - bottomBorder)

    def getOffset(self):
        (leftBorder, bottomBorder)

    def getAbsoluteLocation(self, tileDict, visitedTileIds):
        loc = self.location.getAbsoluteLocation(tileDict, visitedTileIds=visitedTileIds + [self.uid])
        return loc[0] - self.mullions[0], loc[1] - self.mullions[2]

    def getAbsoluteFullDisplayRect(self, tileDict):
        offset = self.location.getAbsoluteLocation(tileDict, [self.uid])
        return Rect(offset[0], offset[1], self.pixelSize[0], self.pixelSize[1])

    def getMaxPixelSize(self):
        return self.pixelSize

    #def getLocalDrawRect(self, tileDict):
    #    offset = self.location.getAbsoluteLocation(tileDict, [self.uid])
    #    return Rect(self.borders[0], self.borders[2], self.pixelSize[0] - self.borders[0] - self.borders[1], self.pixelSize[1] - self.borders[2] - self.borders[3])

class LocalWindow:
    def __init__(self, rect = None, displayStr=":0"):
        if not rect:
            self.rect = Rect(0,0,0,0)
        else:
            self.rect = rect
        self.displayStr=displayStr

    def getDisplayStr(self):
        return self.displayStr

    def getOffset(self):
        return (self.rect.x, self.rect.y)

class MachineDesc:
    def __init__(self, hostname, tiles=None, ipAddress=None, windows=None):
        self.hostname = hostname
        self.ipAddress = None
        if tiles == None:
            self.tiles = []
        else:
            self.tiles = tiles
        self.windows = windows # if None, will be dynamically sized

    def getNumTiles(self):
        return len(self.tiles)

    def __eq__(self, otherMachine):
        if (self.hostname == otherMachine.hostname and
            self.ipAddress == otherMachine.ipAddress and
            self.tiles == otherMachine.tiles):
            return True
        else:
            return False

    def addTile(self, tile):
        self.tiles.append(tile)

    def asDict(self):
        tileList = []
        for tile in self.tiles:
            tileList.append(tile.asDict())
        d = {
          "hostname": self.hostname,
          "ipAddress": self.ipAddress,
          "tiles": tileList 
        }
        return d

class TileConfig:
    def __init__(self, machines = None, tiles = None):
        if machines == None:
            self.machines = []

    def getMachineHostnames(self):
        return [m.hostname for m in self.machines]

    def getNumMachines(self):
        return len(self.machines)

    def __eq__(self, otherConfig):
        if self.machines == otherConfig.machines:
            return True
        else:
            return False

    def addMachine(self, machine):
        self.machines.append(machine)

    def asDict(self):
        machineDictList = []
        for machine in self.machines:
            machineDictList.append(machine.asDict())
        return {"machines":machineDictList}

    def _getTileDict(self):
        tileDict = {}
        for m in self.machines:
            for t in m.tiles:
                tileDict[t.uid] = t
        return tileDict

    def getTileById(self, uid):
        tileDict = self._getTileDict()
        if uid in tileDict:
            return tileDict[uid]
        else:
            return None

    def _getMachineForTile(self, tileId):
        for machine in self.machines:
            for tile in machine.tiles:
                if tile.uid == tileId:
                    return machine
        return None

    def getAbsoluteOffset(self, tileId):
        tileDict = self._getTileDict()
        offset = tiles[tileId].getAbsoluteOffset(tileDict)

    def getAbsoluteFullDisplayRect(self, tileId):
        tileDict = self._getTileDict()
        return tileDict[tileId].getAbsoluteFullDisplayRect(tileDict)

    def getLocalDrawRect(self, tileId):
        tileDict = self._getTileDict()
        machine = self._getMachineForTile(tileId)
        # print "WARNING: getLocalDrawRect not accounting for borders and mullions yet"
        for i in range(len(machine.tiles)):
            tile = machine.tiles[i]
            if tile.uid == tileId:
                return Rect(tile.localOffset[0], tile.localOffset[1], tile.pixelSize[0], tile.pixelSize[1])
        return None

    def getMachineDescByHostname(self, hostname, machineInstanceIndex):
        retMachines = self.getMachineDescsByHostname(hostname)

        if len(retMachines) > 0:
            machineInstanceIndex = min(machineInstanceIndex, len(retMachines)-1)
            return retMachines[machineInstanceIndex]

        errorString = "Could not find hostname: " + hostname + " in list of machines: " + str([x.hostname for x in self.machines])
        print errorString
        raise Exception(errorString)
        return None
          
    def getMachineDescsByHostname(self, hostname):
        retMachines = []
        # really basic string matching
        for machine in self.machines:
            returnMachine = False
            if hostname.lower() == machine.hostname.lower():
                returnMachine = True
            if len(hostname.split(".")) == 1:
                if hostname.lower() == machine.hostname.split(".")[0].lower():
                    returnMachine = True
                #else:
                #    print "FAIL1:", hostname.lower(), machine.hostname.split(".")[0].lower()
            elif len(machine.hostname.split(".")) == 1:
                if hostname.split(".")[0].lower() == machine.hostname.lower():
                    returnMachine = True
                #else:
                #    print "FAIL2", hostname.split(".")[0].lower(), machine.hostname.lower()
            #else:
            #    print "*********** SPLITS:", hostname.split("."), machine.hostname.split(".")
            if returnMachine:
                retMachines.append(machine)
        return retMachines

    def getMainDisplayRect(self):
        tileRects = []
        rects = []
        for machineDesc in self.machines:
            for tile in machineDesc.tiles:
                rects.append(self.getAbsoluteFullDisplayRect(tile.uid))
        rect = Rect(0,0, 0,0)
        for r in rects:
            rect = rect.union(r)
        return rect

    def getLocalWindowFromTileId(self, tileId):
        tileDict = self._getTileDict()
        machine = self._getMachineForTile(tileId)
        for i in range(len(machine.tiles)):
            tile = machine.tiles[i]
            if tile.uid == tileId:
                return tile.localWindowId
        return None

    def getLocalWindowsFromTileId(self, tileId):
        #FIXME: remove this function once unused.
        tileDict = self._getTileDict()
        machine = self._getMachineForTile(tileId)
        localWindows = []
        for i in range(len(machine.tiles)):
            tile = machine.tiles[i]
            if tile.uid == tileId:
                localWindows.append(machine.windows[tile.localWindowId])
        return localWindows

    def getLocalWindowsFromMachineDesc(self, machineDesc):
        localWindows = []
        for tile in machineDesc.tiles:
            localWindowId = self.getLocalWindowFromTileId(tile.uid)
            localWindow = machineDesc.windows[localWindowId]
            localWindows.append(localWindow)
        return localWindows
        

class TileLocation:
    def __init__(self, (offsetX,offsetY), relative = False):
        # relative can be None or: tileId
        self.relative = relative
        self.offset = (offsetX, offsetY)

    def __eq__(self, otherMachine):
        if otherMachine == None:
            return False
        if (self.relative == otherMachine.relative and
            self.offset == otherMachine.offset):
            return True
        else:
            return False

    def asDict(self):
        d = {"relative":self.relative,
             "offset":self.offset}
        return d

    def getAbsoluteLocation(self, tileDict, visitedTileIds):
        if self.relative == False:
            return self.offset
        else:
            if self.relative in visitedTileIds:
                raise Exception("circular location dependency: " + str(self.relative) + str(tileDict[self.relative]))
            tmpOffset = tileDict[self.relative].getAbsoluteLocation(tileDict, visitedTileIds)
            return self.offset[0] + tmpOffset[0], self.offset[1] + tmpOffset[1]

def SaveConfig(tileConfig, filename):

    f = open(filename + ".new", "w")
    outStr = str(tileConfig.asDict())
    outStr = outStr.replace("}", "}\n") + "\n" # make more readable
    f.write(outStr)
    f.close()

    try:
        if os.path.exists(filename):
            shutil.move(filename, filename + ".bak")
    except:
        traceback.print_exc()

    try:
        shutil.move(filename+".new", filename)
    except:
        traceback.print_exc()

def TileLocationFromDict(d):
    return TileLocation(d["offset"], relative=d["relative"])

def TileDescFromDict(d):
    if d["location"] != None:
        locationDict = TileLocationFromDict(d["location"])
    else:
        locationDict = None

    tile = TileDesc( d["pixelSize"], d["localOffset"], d["displayStr"], lrtbBorders=d["borders"], lrtbMullions=d["mullions"], uid=d["uid"], location=locationDict)
    return tile

def MachineDescFromDict(d):
    machine = MachineDesc(hostname=d["hostname"], ipAddress=d["ipAddress"])
    for tileDict in d["tiles"]:
        machine.addTile(TileDescFromDict(tileDict))
    return machine

def TileConfigFromDict(d):
    t = TileConfig()
    machineList = d["machines"]
    for machineDict in machineList:
        t.addMachine(MachineDescFromDict(machineDict))
    return t

def LoadConfig(filename):
    f = open(filename, "r")
    data = f.read()
    print "Read:", len(data)
    d = eval(data)
    return TileConfigFromDict(d)

