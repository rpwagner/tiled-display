
from OpenGL.GL import *
from flapp.pmath.vec3 import Vec3

NumLights = 8  # increase this if supported and needed.

class Light:
    def __init__(self, pos=Vec3(1,1,1), lightIndex=0):
        self.pos = pos
        if lightIndex < 0 or lightIndex >= NumLights:
            raise Exception("InvalidLightIndex: %s" % lightIndex)
        self.lightIndex = lightIndex

    def draw(self, renderer):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0 + self.lightIndex)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glLightfv(GL_LIGHT0 + self.lightIndex, GL_POSITION, self.pos.asTuple())

