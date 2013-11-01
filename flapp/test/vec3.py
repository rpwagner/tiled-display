import sys, os
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flapp.pmath.vec3 import *

v1 = Vec3(1,2,3)
v2 = Vec3(4,5,6)
v3 = Vec3(4,5,6)

assert v2 == v3
assert not (v1 == v2)
assert v1 != v2
assert not (v2 != v3)

assert scaleV3(v2, 2.0) == Vec3(8,10,12)
assert addV3(v2, v3) == Vec3(8,10,12)
v2 += 1
assert v2 == Vec3(5,6,7)

v2 -= 1
assert v2 == v3

assert subV3(v2,Vec3(1,1,1)) == Vec3(3,4,5)

assert v2 != None
assert not (v2 == None)


print "Assertions ok"
