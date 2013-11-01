
import os
import copy
import bluetooth
import sys
import shutil
from mote import Mote

class MoteCache:
    def __init__(self):
        self.cachedDevs = {}

    def read(self, filename="mote.cache"):
        if os.path.exists("mote.cache"):
            cache = open("mote.cache", "r")
            cachedDevs = eval(cache.read())
            print "cachedDevs:", cachedDevs
            for device in cachedDevs:
                self.cachedDevs[device[0]] = Mote(device[0], device[1])
            cache.close()

    def write(self, filename="mote.cache", backupFilename = ".mote.cache.old"):
            cache = open(filename + ".new", "w")
            devList = []
            for devkey, devvalue in self.cachedDevs.items():
                print "Preparing to store:", devkey, devvalue
                devList.append( (devvalue.id, devvalue.name) )
            cache.write(str(devList))
            cache.close()

            try:
                shutil.copy(filename, backupFilename)
            except:
                print "Warning: Unable to copy cache file to back it up."
            try:
                shutil.move(filename + ".new", filename)
            except:
                print "Warning: Unable to move newly created file."

    def addMotes(self, moteTupleList):
        if type(moteTupleList) == type(list()):
            for m in moteTupleList:
                self.cachedDevs[m[0]] = Mote(m[0], m[1])
            
            #if len(moteList) > 0:
            #    if type(moteList[0]) == type(mote.Mote())
            #        for m in moteList:
            #            self.cachedDevs[m.id] = m
        else:
            raise Exception("addMotes expected a list")

    def getMotes(self):
        return copy.copy(self.cachedDevs)

if __name__ == "__main__":
    cache = MoteCache()
    cache.read()
    print cache.getMotes()
    
