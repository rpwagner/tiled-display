
from OpenGL.GL import *
from flapp.pmath.vec3 import Vec3

class BaseNode:
    def __init__(self):
        self.children = []

    def append(self, obj):
        self.children.append(obj)
        obj.parentNode = self

    def pop(self, obj):
        self.children.remove(obj)
        obj.parentNode = None

class PosTransform (BaseNode):
    def __init__(self, x=0, y=0, z=-10):
        BaseNode.__init__(self)
        self.pos = Vec3(x,y,z)

    def draw(self, renderer):
        glPushMatrix()
        pos = self.pos.asTuple()
        glTranslatef(pos[0], pos[1], pos[2])
        for c in self.children:
            c.draw(renderer)
        glPopMatrix()

class EulerTransformDeg(BaseNode):
    def __init__(self, x=0, y=0, z=-10):
        BaseNode.__init__(self)
        self.rot = Vec3(x,y,z)

    def draw(self, renderer):
        glPushMatrix()
        glRotatef(1, 0, 0, self.rot[0])
        glRotatef(0, 1, 0, self.rot[1])
        glRotatef(0, 0, 1, self.rot[2])
        for c in self.children:
            c.draw(renderer)
        glPopMatrix()

