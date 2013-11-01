
class ConfigUI:
    def __init__(self, tileConfig=None):
        self.enabled = False
        self.tileIndex = 0
        self.machineIndex = 0
        self.selectedBorder = "r"
        self.sensitivity = 50
        self.tileConfig=tileConfig

    def toggleOnOff(self):
        self.enabled = not(self.enabled)
        print "configUI enabled:", self.enabled

    def buttonEvent(self, event):
        if event[0] == 2 and event[1]:
            self.tileIndex += 1
            if self.tileIndex >= self.tileConfig.machines[self.machineIndex].getNumTiles():
                self.tileIndex = 0
                self.machineIndex += 1
                if self.machineIndex >= self.tileConfig.getNumMachines():
                    self.machineIndex = 0
            print "machine:tile :", self.machineIndex, self.tileIndex
        if event[1] == True and (event[0] == "r" or event[0] == "l" or event[0] == "u" or event[0] == "d"):
            self.selectedBorder = event[0]
        if event[1] == True and (event[0] == "p" or event[0] == "m"):
            if event[0] == "p":
                value = self.sensitivity
            else:
                value = -self.sensitivity
            if self.selectedBorder == "l":
                lrtb = (value,0,0,0)
            elif self.selectedBorder == "r":
                lrtb = (0,value,0,0)
            elif self.selectedBorder == "t":
                lrtb = (0,0,value,0)
            else: # self.selectedBorder == "b":
                lrtb = (0,0,0,value)
            self.tileConfig.machines[self.machineIndex].tiles[self.tileIndex].modifyMullion(lrtb)
            print "modified mullion:", lrtb, self.machineIndex, self.tileIndex, self.tileConfig.machines[self.machineIndex].tiles[self.tileIndex].getMullion()
        if event[0] == 1 and event[1]:
            if self.sensitivity == 10:
                self.sensitivity == 5
            elif self.sensitivity == 5:
                self.sensitivity == 1
            else:
                self.sensitivity == 10

        if event[0] == "b" and event[1]:
            SaveConfig(self.tileConfig, "tmpConfig.sav")

    def getData(self):
        data = []
        for mach in self.tileConfig.machines:
            for t in mach.tiles:
                tid = t.uid
                data.append( (tid, t.getMullion()) )
        # print "getData:", data
        return data

    def setData(self, data):
        for tileId, lrtb in data:
            tile = self.tileConfig.getTileById(tileId)
            if tile != None:
                if mpi.rank == 1:
                    print "Comparing:", lrtb, tile.getMullion(), tileId
                if lrtb != tile.getMullion():
                    if mpi.rank == 1:
                        print "ConfigUI::setData", ": Set new mullion:", tileId, lrtb, tile.getMullion()
                    #self.tileConfig.machines[mIndex].tiles[tIndex].setMullion(lrtb)
                    tile.setMullion(lrtb)
                    setupLocalConfig(self.tileConfig)
