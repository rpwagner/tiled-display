
import os, sys
from Xlib.display import Display

if "DISPLAY" in os.environ:
    displayStr = os.environ["DISPLAY"]
else:
    displayStr = ":0"

display = Display( displayStr )
screen = display.screen()

x = 0
y = 0
if sys.argv > 1:
    x = int(sys.argv[1])
    if sys.argv > 2:
        y = int(sys.argv[2])
screen.root.warp_pointer(x,y)
print "moved mouse to ", x, ", ", y
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

