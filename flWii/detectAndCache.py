import os
import bluetooth
import sys

from moteCache import MoteCache
from mote import detectMotes

if __name__ == "__main__":
    motes = detectMotes()
    print "Motes:", motes
    if len(motes) > 0:
        cache = MoteCache()
        cache.read()
        cache.addMotes(motes)
        cache.write()

