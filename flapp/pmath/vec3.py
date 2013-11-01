import math

def sumV3(vec):
    return vec.x + vec.y + vec.z

def addV3(vec1, vec2):
    return Vec3(vec1.x+vec2.x, vec1.y+vec2.y, vec1.z+vec2.z)

def subV3(vec1, vec2):
    return Vec3(vec1.x-vec2.x, vec1.y-vec2.y, vec1.z-vec2.z)

def moveV3(vec, amount):
    return Vec3(vec.x+amount, vec.y+amount, vec.z+amount)

def scaleV3(vec, amount):
    return Vec3(vec.x*amount, vec.y*amount, vec.z*amount)

def normV3(vec):
    return scaleV3(vec, 1.0/vec.length())
normalizeV3 = normV3

def dotV3 (v,w):
    # The dot product of two vectors
    return sum( [ x*y for x,y in zip(v,w) ] )

def negV3(v):
    # negative
    return Vec3(-v.x,-v.y,-v.z)

def projectionV3(v,w):
    # The signed length of the projection of vector v on vector w.
    return dotV3(v,w)/w.length()

def crossV3(obj1, obj2):
    return Vec3(obj1.y*obj2.z-obj1.z*obj2.y,
    obj1.z*obj2.x-obj1.x*obj2.z,
    obj1.x*obj2.y-obj1.y*obj2.x)

def squareV3(vec):
    return Vec3(vec.x**2, vec.y**2, vec.z**2)

def rotateAroundVectorV3(v, angleRad, normVec):
    # rotate v around normV3 by angleRad
    cosVal = math.cos(angleRad);
    sinVal = math.sin(angleRad);
    ## (v * cosVal) +
    ## ((normVec * v) * (1.0 - cosVal)) * normVec + 
    ## (v ^ normVec) * sinVal)
    #line1: scaleV3(v,cosVal)
    #line2: dotV3( scaleV3( dotV3(normVec,v), 1.0-cosVal), normVec)
    #line3: scaleV3( crossV3( v,normVec), sinVal)
    #a = scaleV3(v,cosVal)
    #b = scaleV3( normVec, dotV3(normVec,v) * (1.0-cosVal))
    #c = scaleV3( crossV3( v,normVec), sinVal)
    return addV3(
              addV3( scaleV3(v,cosVal),
                     scaleV3( normVec, dotV3(normVec,v) * (1.0-cosVal))
              ),
              scaleV3( crossV3( v,normVec), sinVal)
          )


class Vec3(object):
    __slots__ = ('x','y','z')
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __getitem__(self, index):
        if (index == 0):
            return self.x
        elif (index == 1):
            return self.y
        elif (index == 2):
            return self.z
        raise IndexError("Vector index out of range")

    def __len__(self):
        return 3
    
    def getNorm(self):
        """Return the square length: x^2 + y^2 + z^2"""
        return sumV3(squareV3(self))

    def length(self):
        return math.sqrt(self.getNorm())

    lengthSquared=getNorm

    def __str__(self):
        return str("vec3(%s,%s,%s)" % (self.x, self.y, self.z) )

    def __repr__(self):
        return str("vec3(%s,%s,%s)" % (self.x, self.y, self.z) )

    def __len__(self):
        return 3

    def __eq__(self, v2):
        return hasattr(v2, "x") and self.x == v2.x and self.y == v2.y and self.z == v2.z

    def __ne__(self, v2):
        return not (hasattr(v2, "x") and self.x == v2.x and self.y == v2.y and self.z == v2.z)

    def asTuple(self):
        return (self.x, self.y, self.z)

    def cross(self, obj2):
        return Vec3(self.y*obj2.z-self.z*obj2.y,
            self.z*obj2.x-self.x*obj2.z,
            self.x*obj2.y-self.y*obj2.x)

    def square(self):
        """ square the components """
        self.x **= 2
        self.y **= 2
        self.z **= 2

    def getDataPtr(self):
        return (self.x, self.y, self.z)

    def __iadd__(self, v2):
        if hasattr(v2, "x"):
            self.x += v2.x
            self.y += v2.y
            self.z += v2.z
        else:
            self.x += v2
            self.y += v2
            self.z += v2
        return self

    def __isub__(self, v2):
        if hasattr(v2, "x"):
            self.x -= v2.x
            self.y -= v2.y
            self.z -= v2.z
        else:
            self.x -= v2
            self.y -= v2
            self.z -= v2
        return self
