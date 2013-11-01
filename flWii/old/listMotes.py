import os
import bluetooth
import sys
import shutil

print "performing inquiry..."

nearbyDevices = bluetooth.discover_devices(lookup_names = True)

print "devices found: %s" % len(nearbyDevices)
print nearbyDevices

motes=[]
for device in nearbyDevices:
    if "Nintendo" in device[1]:
        motes.append(device)
        print "Wiimote: ", device[1], device[0]

tmpCache = open("/tmp/mote.cache", "w")
tmpCache.write(str(motes))
tmpCache.close()

if os.path.exists("mote.cache"):
    cache = open("mote.cache", "r")
    cachedDevs = eval(cache.readlines())
    print "cachedDevs:", cachedDevs
    cache.close()
    try:
        shutil.move("mote.cache", "mote.cache.old")
    except:
        print "Unable to move cache file to back it up."
else:
    cachedDevs = []

if len(cachedDevs) == 0:
    print "No motes read from cache"

cache = open("mote.cache", "w")
cache.write(str(cachedDevs + motes))
cache.close()

