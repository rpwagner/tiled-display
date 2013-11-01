
class InputProfile:

    # Input device information,
    #  pointer to its visual representation, and
    #  pointers to the handlers needed to process the input.

    def __init__(self, deviceId=None, deviceType=None):
        self.userProfile = None
        self.visualRepresentation = None
        self.deviceId = deviceId
        self.deviceType = deviceType
        self.inputHandler = None
        self.tileDeviceController = None

    def setInputHandler(self, handler):
        self.inputHandler = handler

    def processInput(self, msgType, argList):
        self.inputHandler.processInput(msgType, argList)

    def setVisualRepresentation(self, obj):
        self.visualRepresentation = obj

    def setTileDeviceController(self, obj):
        self.tileDeviceController = obj

