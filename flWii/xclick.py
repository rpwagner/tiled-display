
import os, time
from Xlib.display import Display
from Xlib.ext import xtest
from Xlib import X

if "DISPLAY" in os.environ:
    displayStr = os.environ["DISPLAY"]
else:
    displayStr = ":0"

display = Display( displayStr )
screen = display.screen()

screen.root.warp_pointer(50,100)
print "moved mouse to 50,50"
#print "display:", dir(display)
#print
#print "screen:", dir(screen)
#print
#print "root window:", dir(screen.root)
#print screen.root.get_geometry()
# help(screen.root)

# Xlib.protocol.display.py lists properties like width_in_pixels.
print "Resolution:", screen.width_in_pixels, screen.height_in_pixels


display.sync()

xtest.fake_input(screen.root, X.ButtonPress, detail=1, x=50, y=100)
display.sync()
xtest.fake_input(screen.root, X.ButtonRelease, detail=1, x=55, y=120)
display.sync()

