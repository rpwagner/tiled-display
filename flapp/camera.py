from OpenGL.GL import *
from OpenGL import GLU

from flapp.pmath.vec3 import *


class Camera:
    def __init__(self):
        self.cameraPos = Vec3(0, 0, 10)
        self.center = Vec3(0, 0, 0)
        self.up = Vec3(0, 1, 0)

    def setPos(self, x,y,z):
        self.cameraPos = Vec3(x,y,z)

    def getPos(self):
        return self.cameraPos

    def setTarget(self, x,y,z):
        self.center = Vec3(x,y,z)
    setCenter=setTarget

    def draw(self, renderer):
        # print "drawing camera"
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        GLU.gluLookAt(
            self.cameraPos[0],self.cameraPos[1],self.cameraPos[2],
            self.center[0],self.center[1],self.center[2],
            self.up[0],self.up[1],self.up[2]
        )

class FollowerCamera(Camera):
    def __init__(self, target, matchTargetDirection=True):
        Camera.__init__(self)
        self.target = target
        self.offset = Vec3(0,0, 3)
        self.targetDistance = 4.0
        self.centerDistance = 10.0
        self.matchTargetDirection=True
        self.dirVec=Vec3(0,0,-1)

    def setOffset(self, offset):
        self.offset = offset
        
    def updateTransform(self, app, secs):
        if self.target:
            if self.matchTargetDirection:
                self.dirVec = self.target.getFacingDirVec()
            self.cameraPos = addV3(addV3(self.target.getPos(), self.offset), scaleV3(negV3(self.dirVec),self.targetDistance))
            #self.center = self.target.getPos()
            self.center = addV3(self.cameraPos, scaleV3(normV3(self.dirVec), self.centerDistance))
            #print "cameraPos:", self.cameraPos, "cameraCenter:", self.center

    def update(self, app, secs):
        self.updateTransform(app, secs)

    def setTarget(self, target):
        self.target = target

    def draw(self, renderer):
        Camera.draw(self, renderer)

    def setTargetDistance(self, dist):
        self.targetDistance = dist


    
