import time, sys
import mote
from moteCache import MoteCache
from mote import Mote

if __name__ == "__main__":
    """
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()
    allDevs = mote.detectAllPossible()

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
    mote.connect()
    """
    mote = Mote(id="00:19:1D:79:93:E0")
    mote.connect()

    mote.setLeds(1,0,0,0)

    mote.startReadThread()
    mote.irBasicModeOn()

    while(1):
        time.sleep(0.1)
        events =  mote.extractButtonEvents()
        if len(events) != 0:
            print events

    mote.disconnect()

