# Univesity of Chicago,
# Feb 2, 2008
# Eric Olson
# adapted from home version written by Eric.

from OpenGL.GL import *
from flapp.pmath.vec3 import *

class ScreenClearer:
    def __init__(self, color=None, clearDepth=True):
        if color == None:
            self.color = (.8, .8, .8, 0.0)
        else:
            if len(color) < 4:
                self.color = (color[0], color[1], color[2], 0.0)
            else:
                self.color = color
        self.clearDepth = clearDepth

    def draw(self, renderer):
        glClearColor(self.color[0], self.color[1], self.color[2], self.color[3])
        if self.clearDepth:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        else:
            glClear(GL_COLOR_BUFFER_BIT)


class pointList:
    P_POINT = 0
    # P_CROSS = 1
    # P_CIRCLE = 2

    def __init__(self):
        self.visible = True
        self.points = [ (0.5, 0.5) ]
        self.color = (0.4, 0.4, 0.9)
        self.diameter = 5
        self.drawType = P_POINT

    def update(self, app, secs):
        pass

    def draw(self, renderer):
        glColor3fv(self.color)
        if self.drawType == P_POINT:
            glPointSize(self.diameter)
            glBegin(GL_POINTS)
            for p in self.points:
                glVertex2f(p[0] * renderer.width, p[1] * renderer.height)
            glEnd()
        else: 
            raise Exception("Unimplemented")


def DrawAxis(length, lineWidth=1):
    glPushAttrib(GL_ENABLE_BIT)
    glLineWidth(lineWidth)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)
    glEnd()

    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, length, 0.0)
    glEnd()

    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, length)
    glEnd()
    glPopAttrib()
        
def DrawTxtrd2dSquareIn2DFromCorner(pt, width, height,  texXMinMax=(0.0, 1.0), texYMinMax=(0.0, 1.0), vflipTexture=False):
    # print "tex coords:", texXMinMax, texYMinMax
    if not vflipTexture:
        glBegin(GL_TRIANGLE_STRIP);
        glTexCoord2f(texXMinMax[0], texYMinMax[1]);
        glVertex2f(pt.x, pt.y+height);
        glTexCoord2f(texXMinMax[0], texYMinMax[0]);
        glVertex2f(pt.x, pt.y);
        glTexCoord2f(texXMinMax[1], texYMinMax[1]);
        glVertex2f(pt.x+width, pt.y+height);
        glTexCoord2f(texXMinMax[1], texYMinMax[0]);
        glVertex2f(pt.x+width, pt.y);
        glEnd();
    else:  # assumes the tex coord is between 0.0 and 1.0
        glBegin(GL_TRIANGLE_STRIP);
        glTexCoord2f(texXMinMax[0], 1.0 - texYMinMax[1]);
        glVertex2f(pt.x, pt.y+height);
        glTexCoord2f(texXMinMax[0], 1.0 - texYMinMax[0]);
        glVertex2f(pt.x, pt.y);
        glTexCoord2f(texXMinMax[1], 1.0 - texYMinMax[1]);
        glVertex2f(pt.x+width, pt.y+height);
        glTexCoord2f(texXMinMax[1], 1.0 - texYMinMax[0]);
        glVertex2f(pt.x+width, pt.y);
        glEnd();

def Draw2dSquareIn2D(pt, width, height):
    glBegin(GL_TRIANGLE_STRIP);
    #a = (pt + size * edge_vec_a);
    #glVertex2fv( a.getDataPtr() );
    glVertex2f( pt.x, pt.y + height)
    #b = (pt + size * edge_vec_b);
    #glVertex2fv( b.getDataPtr() );
    glVertex2f( pt.x, pt.y)
    #c = (pt - size * edge_vec_b);
    #glVertex2fv( c.getDataPtr() );
    glVertex2f( pt.x+width, pt.y+height)
    #d = (pt - size * edge_vec_a);
    #glVertex2fv( d.getDataPtr() );
    glVertex2f( pt.x+width, pt.y)
    glEnd();

def OrthoSetupPush(screenWidth, screenHeight):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screenWidth, 0, screenHeight)
    glMatrixMode(GL_MODELVIEW)

def OrthoSetupPop():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def BlitOne(destPos, destSize):
    glBegin(GL_TRIANGLE_STRIP)
    glVertex2f(destPos.x, destPos.y + destSize[1])
    glVertex2f(destPos.x, destPos.y)
    glVertex2f(destPos.x + destSize[0], destPos.y + destSize[1])
    glVertex2f(destPos.x + destSize[0], destPos.y)
    glEnd()

def BlitColor(destPos, destSize, (screenWidth, screenHeight), color=(0.5, 0.5, 0.5), blend=False, orthoSetup=True):
    glPushAttrib(GL_ENABLE_BIT) # texture, blend
    glDisable(GL_TEXTURE_2D)
    if orthoSetup:
        OrthoSetupPush(screenWidth, screenHeight)
    if len(color) == 3:
        glColor3fv(color)
    elif len(color) == 4:
        glColor4fv(color)
    BlitOne(destPos, destSize)
    if orthoSetup:
        OrthoSetupPop()
    glPopAttrib()

def DrawTxtrd3dSquareIn3DFromCorner(pt, width, height,  texXMinMax=(0.0, 1.0), texYMinMax=(0.0, 1.0)):
    # print "tex coords:", texXMinMax, texYMinMax
    glBegin(GL_TRIANGLE_STRIP);
    glTexCoord2f(texXMinMax[0], texYMinMax[1]);
    glVertex3f(pt.x, pt.y+height, 0);
    glTexCoord2f(texXMinMax[0], texYMinMax[0]);
    glVertex3f(pt.x, pt.y, 0);
    glTexCoord2f(texXMinMax[1], texYMinMax[1]);
    glVertex3f(pt.x+width, pt.y+height, 0);
    glTexCoord2f(texXMinMax[1], texYMinMax[0]);
    glVertex3f(pt.x+width, pt.y, 0);
    print (pt.x, pt.y+height, 0), (pt.x, pt.y, 0), (pt.x+width, pt.y+height, 0), (pt.x+width, pt.y, 0)

    glEnd();

def DrawTxtrd3dSquareIn3DFromCenter(pt, width, height,  texXMinMax=(0.0, 1.0), texYMinMax=(0.0, 1.0)):
    # print "tex coords:", texXMinMax, texYMinMax
    glBegin(GL_TRIANGLE_STRIP);
    glTexCoord2f(texXMinMax[0], texYMinMax[1]);
    glVertex3f(pt.x-width/2., pt.y+height/2., 0);
    glTexCoord2f(texXMinMax[0], texYMinMax[0]);
    glVertex3f(pt.x-width/2., pt.y-height/2., 0);
    glTexCoord2f(texXMinMax[1], texYMinMax[1]);
    glVertex3f(pt.x+width/2., pt.y+height/2., 0);
    glTexCoord2f(texXMinMax[1], texYMinMax[0]);
    glVertex3f(pt.x+width/2., pt.y-height/2., 0);
    #print (pt.x, pt.y+height, 0), (pt.x, pt.y, 0), (pt.x+width, pt.y+height, 0), (pt.x+width, pt.y, 0)
    #print "pt:", pt 
    #print (pt.x-width /2., pt.y+height/2., 0), (pt.x-width/2., pt.y-width/2., 0), (pt.x+width/2., pt.y+height/2., 0), (pt.x+width/2., pt.y-height/2., 0)

    glEnd();

def DrawBillboard3D(pt, width, height, normVec, upVec, texXMinMax=(0.0, 1.0), texYMinMax=(0.0, 1.0) ):
    sideVec = scaleV3(normV3(crossV3(upVec, normVec)), width/2.0)
    upVecB = scaleV3(normV3(upVec), height/2.0)
    #print "pt:", pt 
    #print "norm vec:", normVec
    #print "side vec:", sideVec
    #print "up vec:", upVec
    pt1 = addV3(pt, addV3(negV3(sideVec), upVecB))
    pt2 = addV3(pt, subV3(negV3(sideVec), upVecB))
    pt3 = addV3(pt, addV3(sideVec, upVecB))
    pt4 = addV3(pt, subV3(sideVec, upVecB))
    #print pt1, pt2, pt3, pt4

    glBegin(GL_TRIANGLE_STRIP);
    glTexCoord2f(texXMinMax[0], texYMinMax[1]);
    glVertex3f(pt1.x, pt1.y, pt1.z)
    glTexCoord2f(texXMinMax[0], texYMinMax[0]);
    glVertex3f(pt2.x, pt2.y, pt2.z)
    glTexCoord2f(texXMinMax[1], texYMinMax[1]);
    glVertex3f(pt3.x, pt3.y, pt3.z)
    glTexCoord2f(texXMinMax[1], texYMinMax[0]);
    glVertex3f(pt4.x, pt4.y, pt4.z)
    glEnd();

