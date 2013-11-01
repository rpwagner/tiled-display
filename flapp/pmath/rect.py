
class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return str("Rect(%s,%s,%s,%s)" % (self.x, self.y, self.width, self.height) )

    def __eq__(self, obj):
        return self.x == obj.x and self.y == obj.y and self.width == obj.width and self.height == obj.height

    def __repr__(self):
        return str("Rect(%s,%s,%s,%s)" % (self.x, self.y, self.width, self.height) )

    def union(self, rect):
        x = min(self.x, rect.x)
        y = min(self.y, rect.y)
        width = max(self.x+self.width, rect.x+rect.width) - x
        height = max(self.y+self.height, rect.y+rect.height) - y
        return Rect(x, y, width, height)

    def containsPoint(self, x, y):
        if (x >= self.x and x <= self.x + self.width and 
            y >= self.y and y <= self.y + self.height):
            return True
        else:
            return False

    def setWidth(self, w):
        self.width = w

    def setHeight(self, h):
        self.height = h

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def setOffset(self, x, y):
        self.x = x
        self.y = y

    def setPos(self, x, y):
        self.x = x
        self.y = y

    # TL funcs have 0 based in TL
    def bottomleftTL(self):
        return self.x, self.y+self.height

    bottomleft = bottomleftTL

    def colliderect (self, r2):
        return (((self.x >= r2.x   and self.x < r2.x   + r2.width) or
                 (r2.x   >= self.x and r2.x   < self.x + self.width)) and
                ((self.y >= r2.y   and self.y < r2.y   + r2.height)   or
                 (r2.y   >= self.y and r2.y   < self.y + self.height)))


