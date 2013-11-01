
from flTileMpi import mpi

class AppState:
    # Store application state
    #   Allows syncing with storeDataInDict, and setDataFromDict functions
    def __init__(self):
        self.exitNextFrame=False
        self.exitThisFrame=False

    def storeDataInDict(self, d):
        d["state_exitNext"] = self.exitNextFrame

    def setDataFromDict(self, d):
        self.exitNextFrame=d["state_exitNext"];
        if self.exitNextFrame:
            self.exitThisFrame=True

    def setFlagToExit(self):
        self.exitNextFrame = True
        if mpi.procs < 2:           # don't need to wait until next frame
            self.exitThisFrame = True  #  if  this is the only proc

    def getFlagToExit(self):
        return self.exitThisFrame
        

