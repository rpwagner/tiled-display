import time, sys, os

from mote import detectAllPossible
from moteCache import MoteCache
from mote import Mote
import traceback

def connectToMote(moteId="", led=(1,0,0,0) , changeOnly=False):
    """
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()
    allDevs = detectAllPossible()

    selectedMoteId = None
    for d in allDevs:
        if d in cache.getMotes():
            selectedMoteId = d
            break

    if selectedMoteId == None:
        print "No motes found.  Device ids:", allDevs, "cacheMoteIds:", cache.getMotes().keys()
        sys.exit()

    # mote = cache.getMotes().values()[0]
    mote = cache.getMotes()[selectedMoteId]
    """

    #if moteId == "":
    #    moteId = "00:17:AB:32:BF:EF"
    #mote = Mote(id="00:19:1D:79:93:E0")
    #mote = Mote(id="00:17:AB:32:BF:EF")
    mote = Mote(id=moteId)
    mote.connect()

    #mote.setLeds(1,0,0,0)
    if mote.connected:
        mote.setLeds(led[0], led[1], led[2], led[3])
        mote.startReadThread()
        mote.irBasicModeOn(changeOnly=changeOnly)
    return mote

if __name__ == "__main__":
    connectToMote()
