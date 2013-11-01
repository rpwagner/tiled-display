
try:
    from airstream.client import InputClientFactory
except Exception, e:
    import traceback
    traceback.print_exc()
    print "Unable to import airstream"
    raise e
from inputProfile import InputProfile
from genericInputMapper import GenericInputMapper
from airstream.asTypes import *
from tileMote import TileMousePosition
from mouseUpdater import TileDeviceController

class AirstreamInputAndEventProcessor:
    #  receives inputs, finds out which inputProfile they apply to.
    #     if the inputProfile or its userProfile has a use for the 
    #     input event, they will use it.
    #     e.g. if inputProfile has a visualRepresentation, a mouse
    #       pos event will set its position.

    def __init__(self, regionRect, app=None, visualsManager=None, host="localhost", port=11000):
        self.connected = False
        self.inputDevices = {} # inputProfile stored by deviceId
        self.app = app
        self.visualsManager = visualsManager
        self.regionRect = regionRect # for things like display width and height
        self.inputClientFactory = None
        self.host=host
        self.port=port

    def initialize(self):
        try:
            f = InputClientFactory()
            self.inputClientFactory = f

            f.setConnectionMadeCallback(self.newConnection)
            f.setReceiveCallback(self.receive)
            f.setConnectFailedCallback(self.connectFailed)
            f.setConnectionLostCallback(self.connectionLost)

            self._netConnect()
        except:
            traceback.print_exc()

    def _netConnect(self):
        print "Connecting to ", self.host, self.port
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, self.inputClientFactory)

    def connectionLost(self, reason):
        print "connection to input service lost, will try again in 5 seconds)"
        from twisted.internet import reactor
        reactor.callLater(5.0, self._netConnect )

    def connectFailed(self, reason):
        print "connection to input service failed, will try again in 5 seconds)"
        from twisted.internet import reactor
        reactor.callLater(5.0, self._netConnect )

    def update(self, secs):
        pass

    def setVisualsManager(self, manager):
        self.visualsManager = manager

    def newConnection(self, client):
        self.connected = True;
        print "Connected to input service"

    def setupNewDevice(self, deviceId, deviceType):
        inputProfile = InputProfile(deviceId, deviceType)

        # get a new cursor image
        simpleAvatar = self.visualsManager.setupNewVisualRepresentation()

        # Setup a mouse-like handler to filter mouse coords to prevent jitter
        # and convert the coords into display coordinates.
        # This will receive the inputs and set the simpleAvatar (cursor)  position.
        tileMousePos = TileMousePosition(simpleAvatar, self.regionRect.width, self.regionRect.height)
        if deviceType in [DT_WII,DT_WIIMOUSE]:
            print "DEVICE WITH FILTER:", deviceType
            tileMousePos.useFilter = True
        else:
            print "DEVICE WITH NO FILTER:", deviceType
            tileMousePos.useFilter = False

        # FIXME, change next line to tileDeviceController = TileDeviceController(tileMousePos, visualsManager, configUI=None)
        tileDeviceController = TileDeviceController(tileMousePos, inputManager=self, configUI=None, renderers=self.visualsManager.renderers, masterObjects=self.visualsManager.masterObjectList, cursorListList=self.visualsManager.cursorListList)

        #def tmpSetMousePosNormalized(x,y):
        #    tileMousePos.setMousePosNormalized(x,y)
        #    tileDeviceController.updateTargetPos()

        # setup a callback to handle new events
        #inputMapper = PositionalInputMapper(target=tileMousePos)
        #inputMapper.mapMsgTypeToTargetControl(MT_XY, "setMousePosNormalized")  #should also work
        inputMapper = GenericInputMapper(target=tileMousePos)   
        #inputMapper.mapMsgTypeToCallback(MT_XY, tileMousePos.setMousePosNormalized)
        #inputMapper.mapMsgTypeToCallback(MT_XY, tmpSetMousePosNormalized)
        inputMapper.mapMsgTypeToCallback(MT_XY, tileDeviceController.setMousePosNormalized)
        inputMapper.mapMsgTypeToCallback(MT_BUTTONDOWN, tileDeviceController.mouseButtonDownEvent)
        inputMapper.mapMsgTypeToCallback(MT_BUTTONUP, tileDeviceController.mouseButtonUpEvent)
        inputMapper.mapMsgTypeToCallback(MT_STRING, tileDeviceController.stringEvent)
        inputMapper.mapMsgTypeToCallback(MT_KEYDOWN, tileDeviceController.keyDownEvent)
        inputProfile.setInputHandler(inputMapper)

        inputProfile.setVisualRepresentation( simpleAvatar )
        inputProfile.setTileDeviceController( tileDeviceController )
        self.inputDevices[deviceId] = inputProfile

        return inputProfile

    def receive(self, data):
        try:
            # print "InputAndEventProcessor received:", data
            dataParts = data.split(",")
            deviceType, deviceId, msgType = dataParts[:3]

            try:  # make sure we know about this device
                inputProfile = self.inputDevices[deviceId]
            except KeyError:
                inputProfile = self.setupNewDevice(deviceId, deviceType)

            #if 99999 != msgType: # replace 9999 with checks for things that need
                                 # to be done immediately.
            #    # asynchronous so we don't need to queue
            #    #self.queueEvent(inputProfile, msgType, dataParts[3:]
            self.handleEvent(inputProfile, int(msgType), dataParts[3:])
        except:
            import traceback
            traceback.print_exc()
            #import debugFile
            #debugFile.write(traceback.format_exc())
            #debugFile.flush()
            #of.write(traceback.format_exc)
            #of.flush()

    def handleEvent(self, inputProfile, msgType, payload):
        inputProfile.processInput( msgType, FormatMsgPayload(msgType, payload) ) # visualRepr.setPos( FormatPayload(payload) )
        """
        if None != inputProfile.visualRepr:
            if MT_XY == msgType: # mousemove
                inputProfile.processInput( FormatPayload(payload) ) # visualRepr.setPos( FormatPayload(payload) )
            elif MT_BUTTONEVENT == msgType: # mousebutton
                pass
            elif MT_BUTTONUPEVENT == msgType: 
                pass
            elif MT_KEYDOWNEVENT == msgType:
                pass
            elif MT_KEYUPEVENT == msgType:
                pass
        """

