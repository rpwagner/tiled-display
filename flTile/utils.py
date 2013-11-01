class CursorAutoMover:
    def __init__(self, target, xrange=(0,5000), yrange=(0,3000), xvel=100, yvel=100):
        self.target = target
        self.xvel = xvel
        self.yvel = yvel
        self.xrange  = xrange
        self.yrange  = yrange
        self.visible = False

    def draw(self):
        pass

    def update(self, secs, app):
        posTuple = self.target.getPos()
        pos = Vec2(posTuple[0], posTuple[1])
        pos.x = pos.x + self.xvel * secs
        pos.y = pos.y + self.yvel * secs
        if pos.x > self.xrange[1]:
            self.xvel = -abs(self.xvel)
        if pos.y > self.yrange[1]:
            self.yvel = -abs(self.yvel)

        if pos.x < self.xrange[0]:
            self.xvel = abs(self.xvel)
        if pos.y < self.xrange[0]:
            self.yvel = abs(self.yvel)

        self.target.setPos(pos.x, pos.y)
        # print "pos:", pos.x, pos.y
