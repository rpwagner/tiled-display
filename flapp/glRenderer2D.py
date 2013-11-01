from OpenGL.GL import *
from OpenGL.GLU import *

class glRenderer2D:
    def __init__(self, multipleRenderers=False, firstRenderer=True):
        self.objects = []
        self.objectIds = {}
        self.idsObjects = {}
        self.nextObjectId = 1
        self.renderOrder = []
        self.glSetupObjs = []
        self.translucentObjects = []
        self.frameSetupObjs = []
        self.firstRenderer = firstRenderer
        self.viewportRect = None
        self.multipleRenderers = multipleRenderers

    def render(self):
        if self.multipleRenderers:
            self.setupFrame()
        for obj in self.frameSetupObjs:
            #print "renderer draw obj:", obj.__class__.__name__
            obj.draw(self)
        # print "Renderer objects to draw:", self.objects
        if len(self.renderOrder) > 0:
            #keys = self.idsObjects.keys()
            #keys.sort()
            #for id_key in keys: # self.idsObjects:
            for id_key in self.renderOrder:
                try:
                    obj = self.idsObjects[id_key]
                    obj.draw(self)
                except KeyError:
                    print "glRenderer2D:render(), order KeyError: ", id_key
        else:
            for obj in self.objects:
                obj.draw(self)

    def getObjectById(self, objId):
        if objId in self.idsObjects:
            return self.idsObjects[objId]
        else:
            return None

    draw = render

    def addFrameSetupObj(self, obj):
        self.frameSetupObjs.append(obj)

    def setRenderOrder(self, order):
        self.renderOrder = order

    def addGlSetupObj(self, obj):
        self.glSetupObjs.append(obj)

    def bringObjToFront(self, obj):
        #if obj in self.objectIds:
        objId = self.objectIds[obj]
        self.bringIdToFront(objId)

    def bringIdToFront(self, objId):
        self.renderOrder.remove(objId)
        self.renderOrder.append(objId)

    def sendObjToBack(self, obj):
        #if obj in self.objectIds:
        objId = self.objectIds[obj]
        self.sendIdToBack(objId)

    def sendIdToBack(self, objId):
        self.renderOrder.remove(objId)
        self.renderOrder.insert(0,objId)

    def addObject(self, obj):
        self.objects.append(obj)
        self.objectIds[obj] = self.nextObjectId
        self.idsObjects[self.nextObjectId] = obj
        self.renderOrder.append(self.nextObjectId)
        self.nextObjectId += 1
        # FIXME haven't added renderOrder code to "removeObject()" yet

    def getRenderOrder(self):
        return self.renderOrder

    def addDynamicObject(self, obj):
        self.addObject(obj) #self.objects.append(obj)

    def addStaticObject(self, obj):
        self.addObject(obj) # self.objects.append(obj)

    def removeStaticObject(self, obj):
        self.objects.remove(obj)

    def removeDynamicObject(self, obj):
        self.objects.remove(obj)

    def init(self, windowWidth, windowHeight, viewportRect=None):
        self.viewportRect = viewportRect
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        if self.viewportRect != None:
            self.width = self.viewportRect.width
            self.height = self.viewportRect.height
        else:
            self.width = self.windowWidth
            self.height = self.windowHeight
        self.reshape(self.width, self.height, self.viewportRect)

        try:
            # Some of the render objects use glut so initialize it (possibly
            #  only needed for freeglut)
            if self.firstRenderer:
                from OpenGL import GLUT
                # GLUT.glutInit([])
        except Exception, e:
            print "Note: glut not able to be initialized.  glut functions not available:", e

        glDisable(GL_DEPTH_TEST)        #use our zbuffer
        glDisable(GL_LIGHTING)        #use our zbuffer

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

    def setupFrame(self):
        if (self.viewportRect != None):
            # print "viewport:", self.viewportRect
            glViewport(self.viewportRect.x, self.viewportRect.y,
                       self.viewportRect.width, self.viewportRect.height)
            glEnable(GL_SCISSOR_TEST)
            glScissor(self.viewportRect.x, self.viewportRect.y,
                       self.viewportRect.width, self.viewportRect.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)


    def reshape(self, w, h, viewportRect=None):
        if (viewportRect != None):
            print "viewport:", viewportRect
            glViewport(viewportRect.x, viewportRect.y, viewportRect.width, viewportRect.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.width=w
        self.height=h
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)

