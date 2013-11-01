import time, sys
import mote
from moteCache import MoteCache

if __name__ == "__main__":
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

    mote.setLeds(1,0,0,0)

    mote.startReadThread()

    mote.irBasicModeOn()

    printPoints = False
    if "print" in sys.argv:
        printPoints = True

    while(1):
        if printPoints:
            pts = mote.extractNormalizedPoints() 
            if len(pts) > 0:
                print pts
        time.sleep(1)

    mote.disconnect()

