from OpenGL.GL import *
from OpenGL import GLUT

from flapp.glDrawUtils import DrawAxis

class Axis:
    def __init__(self, length=1.0):
        self.length = length

    def update(self, app, secs):
        pass

    def draw(self, renderer):
        DrawAxis(self.length)

