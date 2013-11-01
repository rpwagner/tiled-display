import math
from math import sin, cos
import numarray
from OpenGL.GL import *
from flapp.pmath.vec3 import *
from flapp.glDrawUtils import DrawAxis

class GlobeLayer:
    def __init__(self, latSize, lonSize):
        self.latSize = latSize
        self.lonSize = lonSize
        print "Creating layer:", self.latSize, " x " , self.lonSize
        self.heights = numarray.array([[0.0]*self.latSize]*self.lonSize, type=numarray.Float32)

class GlobeData:
    def __init__(self, radius=6377830., heightsPerUnit = 0.000001):
        self.layer1 = GlobeLayer(4, 4)
        self.layer2 = GlobeLayer(8, 8)
        self.layer3 = GlobeLayer(16, 16)
        self.layers = [None, self.layer1, self.layer2, self.layer3]

    def getLayer(self, index):
        return self.layers[index]

class Globe:
    def __init__(self, globeData, radius=6377830., heightsPerUnit = 0.000001):
        # Earth radius is 6,377,830 meters.  For now make this similarly sized
        self.radius = radius
        self.circumference = 2 * math.pi * self.radius
        self.globeData = globeData
        # lat range is -90 90 --> array[180]
        # lon range is -180 180 --> array[360]
        # self.latSizeLayer1 = int(round(self.circumference / 2.0 * heightsPerUnit))
        # self.lonSizeLayer1 = int(round(self.circumference * heightsPerUnit))
        self.camera = None
        self.drawLayerIndex = 2 # for debug drawing

    def setCamera(self, camera):
        self.camera = camera

    def _latLonToCartesian(self, lat, lon, alt):
        zenith = 90 - lat
        azimuth = lon
        x = alt * sin (zenith) * cos (azimuth)
        y = alt * sin (zenith) * sin (azimuth)
        z = alt * cos (zenith)
        return Vec3(x,y,z)

    def drawFull(self, renderer):
        # latStep = 10.0
        # lonStep = 25.0
        DrawAxis(self.radius)

        layer = self.globeData.getLayer(self.drawLayerIndex)

        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_LIGHTING)
        glColor3f(0,0,0.5)
        #for lat in range(-90, 90, latStep):
        #    for lon in range(-180, 180, lonStep):
        # coords = []
        for latIndex in range(layer.latSize-1):
            lat = (float(latIndex) / layer.latSize * 180) - 90.
            higherLat = ( (latIndex+1) / layer.latSize * 180) - 90.
            glBegin(GL_TRIANGLE_STRIP)
            for lonIndex in range(4): # range(layer.lonSize):
                lon = (float(lonIndex) / layer.lonSize * 360) + -180.
                # print higherLat, lon
                cartPos1 = self._latLonToCartesian(lat, lon, self.radius + layer.heights[latIndex][lonIndex])
                glNormal3fv(normalizeV3(cartPos1).asTuple()) # cartPos - vec(0,0,0)
                glVertex3fv(cartPos1.asTuple())

                cartPos2 = self._latLonToCartesian(higherLat, lon, self.radius + layer.heights[latIndex+1][lonIndex])
                glNormal3fv(normalizeV3(cartPos2).asTuple())
                glVertex3fv(cartPos2.asTuple())
                # coords.append ( cartPos1, cartPos2 )
            glEnd()

        # print "Draw globe coords:", coords

        glPopAttrib()

    draw = drawFull

    def getHeightAtLatLong(self, lat, lon):
        # lat 0 == equator
        # lat 90N (+90) == north pole
        # lat 90S (-90) == south pole
        # lon 0 == prime meridian
        # 180W (-180) and 180E (+180) is antipodal meridian

        # *** convert lat to array coordinate
        # convert lat and lon to 0-1 range
        normLat = ((lat + 90 ) % 180.) / 180.
        normLon = ((lon + 180 ) % 360.) / 360.
        latIndex = round(normLat * self.latSizeLayer1)
        lonIndex = round(normLon * self.lonSizeLayer1)
        return self.heightsLayer1[lat][lon]

    getHeight = getHeightAtLatLong
