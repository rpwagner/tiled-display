
from ctypes import *
import os


# Add a callback object so it's easier to use outside of this class
global gCallbackObj
gCallbackObj=None
def registerCallbackObj(obj):
    global gCallbackObj
    gCallbackObj = obj
    # callbackObj should implement newDataXY(self, x,y), etc.

# --- The functions that will be called.
def NewDataXY(x,y):
    if gCallbackObj:
        gCallbackObj.newDataXY(x,y)
    else:
        print "mouseMoved:", x,y

"""
def NewDataXYArray(values):
    print "newDataXYArray:", values
    #for i in range(len(values)/2):
    #    x=i*2
    #    y=i*2+1
    #    print "mouseMoved:", x,y
"""

def ButtonDown(btnId, x,y):
    if gCallbackObj:
        gCallbackObj.buttonDown(btnId,x,y)
    else:
        print "buttonDown:", btnId, x,y

def ButtonUp(btnId, x,y):
    if gCallbackObj:
        gCallbackObj.buttonUp(btnId,x,y)
    else:
        print "buttonUp:", btnId, x,y

# --- Setup callbacks from C

# define callbacks
XYFUNC = CFUNCTYPE(c_void_p, c_float, c_float)
BUTTONFUNC = CFUNCTYPE(c_void_p, c_int, c_float, c_float)

# create c callable callback
xyfunc = XYFUNC(NewDataXY)
buttondownfunc = BUTTONFUNC(ButtonDown)
buttonupfunc = BUTTONFUNC(ButtonUp)

def setupLib():
    # Setup
    libtest = cdll.LoadLibrary(os.getcwd() + '/libTestDataSrc.so')

    # tell the library about the callbacks
    libtest.setCallbacks(xyfunc, buttondownfunc, buttonupfunc)

    return libtest

def main():
    libtest = setupLib()

    # test it
    for i in range(3): 
        libtest.update()

if __name__ == "__main__":
    main()    

