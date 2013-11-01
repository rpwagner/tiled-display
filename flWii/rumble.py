import time
import mote
from moteCache import MoteCache

if __name__ == "__main__":
    cache = MoteCache()
    cache.read()

    # print "GetMotes:", cache.getMotes()

    mote = cache.getMotes().values()[0]
    mote.connect()
    mote.rumbleOn()
    time.sleep(1)
    mote.rumbleOff()
    time.sleep(1)
    mote.disconnect()

