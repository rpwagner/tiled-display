import os, sys, time
sys.path = ["..", "."] + sys.path

from moteKeysAndMouse import MoteX11WithKeysAndMouse

if len(sys.argv) > 1:
    btn = sys.argv[1]
else:
    btn = 'c'
print "Button to be pressed: \"%s\"" % btn

x=MoteX11WithKeysAndMouse()

x.connectToX()

print "pressing key"
x.sendKeyPress(btn)
time.sleep(0.0001)
print "releasing key"
x.sendKeyRelease(btn)

print "waiting to exit"
time.sleep(1)
