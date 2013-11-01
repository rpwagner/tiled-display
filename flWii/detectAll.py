from moteCache import MoteCache
from mote import detectAllPossible

if __name__ == "__main__":
    devices = detectAllPossible()
    print "Devices:", devices

