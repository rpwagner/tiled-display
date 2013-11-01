
# Device types
DT_INVALID = 0
DT_POINTER = 1 # generic mouse-like device
DT_WIIMOUSE = 2
DT_WII = 3

# Message types
MT_INVALID = 0
MT_XY = 1              # x, y

### DEPRECATED NAMES
MT_BUTTONEVENT = 2     # x, y, btnId
MT_BUTTONUPEVENT = 3     # x, y, btnId
MT_KEYDOWNEVENT = 4    # key, x, y
MT_KEYUPEVENT = 5      # key, x, y

### CURRENT NAMES
MT_BUTTONDOWN = 2     # x, y, btnId
MT_BUTTONUP = 3     # x, y, btnId
MT_KEYDOWN = 4    # key, x, y
MT_KEYUP = 5      # key, x, y

# Other possibilities
MT_STRING = 6
#MT_INTARRAY = 6
#MT_FLOATARRAY = 7
#MT_JSON = 8

MT_DONTSENDDATA = 100
MT_SENDDATA = 101

BTN_LEFT = 0
BTN_MIDDLE = 1
BTN_RIGHT = 2

def FormatMsgPayload(msgType, argList):
    if msgType in [MT_XY]:
        return [float(i) for i in argList]
    elif msgType in [MT_BUTTONDOWN, MT_BUTTONUP]:
        return [ float(argList[0]), float(argList[1]), int(argList[2]) ]
    elif msgType in [MT_KEYDOWN, MT_KEYUP]:
        return [argList[0]] + [float(i) for i in argList[1:]]
    elif msgType in [MT_STRING]:
        return [argList[0]]
    else:
        print "WARNING: FormatMsgPayload(), unhandled msgType.", msgType
        return argList

