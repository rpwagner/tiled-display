from OpenGL import GL, GLU
from OpenGL.GL import *
from flapp.camera import Camera


class glRenderer3D:
    def __init__(self):
        self.objects = []
        self.initted = False
        self.nearDist = 0.001
        self.farDist = 1000.0
        self.glSetupObjs = []
        self.frameSetupObjs = []
        self.translucentObjects=[]
        self.screenObjects=[]
        self.fov=45
        self.camera = Camera()

    def addRenderObject(self, obj):
        self.objects.append(obj)

    def addDynamicObject(self, obj):
        self.objects.append(obj)

    def addStaticObject(self, obj):
        self.objects.append(obj)

    def removeStaticObject(self, obj):
        self.objects.remove(obj)

    def removeDynamicObject(self, obj):
        self.objects.remove(obj)

    def init(self, width, height):
        self.width = width
        self.height = height
        self.reshape(self.width, self.height)

        # Some of the render objects use glut so initialize it (possibly
        #  only needed for freeglut)
        from OpenGL import GLUT
        GLUT.glutInit([])

        for obj in self.glSetupObjs:
            #print "renderer init draw glSetupObj:", obj.__class__.__name__
            obj.draw()

        for obj in self.objects + self.translucentObjects:
            #print "renderer init obj.glInit:", obj.__class__.__name__
            try:
                obj.glInit()
            except AttributeError:
                pass

        self.initted = True

    def reshape(self, w, h):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        self.width=w
        self.height=h
        GLU.gluPerspective(self.fov, self.width * 1.0 / self.height, self.nearDist, self.farDist)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def setCamera(self, cam):
        self.camera = cam

    def addFrameSetupObj(self, obj):
        self.frameSetupObjs.append(obj)

    def addGlSetupObj(self, obj):
        self.glSetupObjs.append(obj)

    def render(self, objects=[]):
        for obj in self.frameSetupObjs:
            #print "renderer draw obj:", obj.__class__.__name__
            obj.draw(self)

        if (None != self.camera):
            #print "renderer draw obj:", obj.__class__.__name__
            self.camera.draw(self)

        for o in self.objects + objects:
            #print "renderer draw obj:", obj.__class__.__name__
            o.draw(self)

        GL.glDepthMask(GL.GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for o in self.translucentObjects:
            #glMatrixMode(GL_MODELVIEW)
            #glLoadIdentity()
            #self.camera.draw()
            #print "renderer draw obj:", obj.__class__.__name__
            try:
                o.draw(self)
            except:
                traceback.print_exc()
                sys.exit()
        glDisable(GL_BLEND)

        GL.glDepthMask(GL.GL_TRUE)

        self._renderScreenObjects()

        # GL.glFlush()
    draw=render

    def _renderScreenObjects(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GLU.gluOrtho2D(0,self.width,0,self.height)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glPushAttrib(GL_ENABLE_BIT)
        GL.glDisable(GL_LIGHTING);
        GL.glDisable(GL_DEPTH_TEST);

        for o in self.screenObjects:
            o.draw(self) # pass renderer so screen parameters are available

        GL.glPopAttrib() # GL_ENABLE_BIT
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()


