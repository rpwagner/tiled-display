import os
from Xlib.display import Display

class Rect:
    def __init__(self, offsetX, offsetY, width, height):
        self.x = offsetX
        self.y = offsetY
        self.width = width
        self.height = height

class MoteX11:
    def __init__(self):
        if "DISPLAY" in os.environ:
            self.displayStr = os.environ["DISPLAY"]
        else:
            self.displayStr = ":0"
        self.rect = None
        self.printInfo = True

    def connectToX(self):
        self.display = Display( self.displayStr )

        self.displayWidth = self.display.screen().width_in_pixels
        self.displayHeight = self.display.screen().height_in_pixels
  
        self.rect = Rect(0,0,self.displayWidth, self.displayHeight)

    def setWarpRect(self, (offsetX, offsetY), (width, height)):
        self.rect = Rect(offsetX,offsetY, self.displayWidth, self.displayHeight)

    def setMousePos(self, x, y):
        self.display.screen().root.warp_pointer(x,y)
        self.display.sync()

    def setMousePosNormalized(self, x, y):
        # x and y arguments should be between 0 and 1
        if self.printInfo:
            print "x,y:", int(self.rect.x + self.rect.width * x), int(self.rect.y + self.rect.height * y)
        self.display.screen().root.warp_pointer(int(self.rect.x + self.rect.width * x), int(self.rect.y + self.rect.height * y))
        self.display.sync()
