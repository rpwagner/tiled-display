
class ObjType:
    INVALID=0
    UNSPECIFIED=1
    STREAM=2
    GROUPED_STREAM=3
    TILED_MOVIE_WITH_LAYOUT=4

class ObjectDescription:
    def __init__(self, type=ObjType.UNSPECIFIED):
        self.type = type

class StreamProtocols:
    INVALID=0
    UNSPECIFIED=1
    FLX_H261=2
    CELERITAS_TCP_RAW=3

class StreamObjDescription(ObjectDescription):
    def __init__(self, protocol, (streamWidth, streamHeight), vflip=False):
        ObjectDescription.__init__(self, type=ObjType.STREAM)
        self.protocol = protocol
        self.streamWidth = streamWidth
        self.streamHeight = streamHeight
        self.vflip=vflip

class GroupedStreamObjDescription(ObjectDescription):
    def __init__(self, protocol, (streamWidth, streamHeight), vflip=False):
        ObjectDescription.__init__(self, type=ObjType.GROUPED_STREAM)
        self.protocol = protocol
        self.streamWidth = streamWidth
        self.streamHeight = streamHeight
        self.vflip=vflip
    

