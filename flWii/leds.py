import time
import mote
from moteCache import MoteCache

ledTuples = [
(1,0,0,0),
(0,1,0,0),
(0,0,1,0),
(0,0,0,1),

(1,1,0,0),
(0,1,1,0),
(0,0,1,1),
(1,1,1,0),
(0,1,1,1),
(1,0,1,0),
(0,1,0,1),
(1,0,0,1),
(1,1,0,1),
(1,0,1,1),
(1,1,1,1),

]

def LedTupleFromIndex(i):
     
    return  ledTuples[i % len(ledTuples) ]

if __name__ == "__main__":
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()

    mote = cache.getMotes().values()[0]
    mote.connect()
    mote.setLeds(1,0,0,0)
    time.sleep(2)
    mote.setLeds(0,1,0,0)
    time.sleep(2)
    mote.setLeds(0,0,1,0)
    time.sleep(2)
    mote.setLeds(0,0,0,1)
    time.sleep(2)
    mote.setLeds(1,1,1,1)
    time.sleep(2)
    mote.setLedsOff()
    time.sleep(1)
    mote.disconnect()

