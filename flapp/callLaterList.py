# Written by Eric Olson
# License: GPLv3 or BSD

import time
import traceback

class CallLaterList:
    def __init__(self):
        self.callLaters = []

    def add(self, secs, func, args=None, currentTime = None):
        if args == None:
            args = []
        if currentTime == None:
            currentTime = time.time()
        self.callLaters.append( (currentTime + secs, func, args, currentTime, secs) )
        self.callLaters.sort()

    def getAndRemove(self, currentTime=None):
        if currentTime == None:
            currentTime = time.time()
        # assume sorted since we sort everytime something's added
        onesToCall = []
        while len(self.callLaters) > 0 and self.callLaters[0][0] < currentTime:
            onesToCall.append(self.callLaters.pop(0))

        return onesToCall

    def checkCallAndRemove(self, currentTime=None):
        if currentTime == None:
            currentTime = time.time()
        # assume sorted since we sort everytime something's added
        onesToCall = []
        while len(self.callLaters) > 0 and self.callLaters[0][0] < currentTime:
            onesToCall.append(self.callLaters.pop(0))

        for tup in onesToCall:
            try:
                func = tup[1]
                args = tup[2]
                func(*args)
            except:
                print "EXCEPTION callLaterList"
                traceback.print_exc()

