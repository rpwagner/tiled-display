import simplejson     # MIT license
# import python-cjson # LGPL license, not used

if __name__ == "__main__":
    import sys, os
    sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path

from flapp.pmath.vec3 import Vec3

# Encoding
class FlappJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Vec3):
            # note: order of args is different than the order in the xml schema
            #   but the same order of the constructor args. (simpler, slightly faster)
            return {"__vec3__": [obj.x, obj.y, obj.z]}
        return simplejson.JSONEncoder.default(self, obj)


# Decoding
def ReconstructFlappObject(dct):
    if '__vec3__' in dct:
        args = dct['__vec3__']
        return Vec3(*dct['__vec3__'])
    return dct

class FlappJsonTranslator:
    def serialize(self, data):
        # print "serializing:", data, FlappJsonEncoder().encode(data)
        return FlappJsonEncoder().encode(data)
        # The following two should be equivalent
        #   dumps(data, cls=ComplexEncoder)
        #   FlappJsonEncoder().encode(data)

    def deserialize(self, data):
        return simplejson.loads(data, object_hook=ReconstructFlappObject)


if __name__ == "__main__":
    trans = FlappJsonTranslator()
    e = Vec3(1,2,3)
    print "Original object:", e
    serializedData = trans.serialize(e)
    print "serialized:", type(serializedData), serializedData
    pyObject = trans.deserialize(serializedData)
    print "reconstructed:", pyObject

