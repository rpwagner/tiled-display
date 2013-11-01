
import traceback
from inputMapper import InputMapper

class GenericMsgCallback:
    # Holds a callback function, a "type" and "arguments" for it, and
    #   whether the callback expects the type and arguments.
     
    def __init__(self, callback, passMsgType=False, passMsgArgs=True, extraArgs=None):
        self.callback = callback
        self.passMsgType=passMsgType
        self.passMsgArgs=passMsgArgs
        if extraArgs == None:
            self.extraArgs = []
        else:
            self.extraArgs=extraArgs

        # only self.call will be used
        # setup a simpler callback to avoid if tree for every input msg.
        if passMsgType and passMsgArgs:
            self.call = self._callWithMsgTypeAndArgs
        elif passMsgType and not passMsgArgs:
            self.call = self._callWithMsgTypeNoArgs
        elif not passMsgType and passMsgArgs:
            self.call = self._callWithNoMsgTypeWithArgs
        elif not passMsgType and not passMsgArgs:
            self.call = self._callWithNoMsgTypeNoArgs

    def _callWithMsgTypeAndArgs(self, msgType, msgArgList):
        argList = [msgType] + msgArgList + self.extraArgs
        self.callback(*argList)
    def _callWithMsgTypeNoArgs(self, msgType, msgArgList):
        argList = [msgType] + self.extraArgs
        print "CALLING WITH ARGLIST:", argList
        self.callback(*argList)
    def _callWithNoMsgTypeWithArgs(self, msgType, msgArgList):
        argList = msgArgList + self.extraArgs
        self.callback(*argList)
    def _callWithNoMsgTypeNoArgs(self, msgType, msgArgList):
        self.callback(*self.extraArgs)

    call = _callWithNoMsgTypeWithArgs # overridden during initialization


class GenericInputMapper(InputMapper):
    # Maps an input type to a callback
    # Will processInput() to call the callback()
    def __init__(self, target=None):
        InputMapper.__init__(self)
        self.target = target
        self.inputMap = {} # maps inputs to controls

    def mapMsgTypeToTargetControl(self, msgType, controlName, passMsgType = False, passMsgArgs = True, extraArgs=None):
        callbackFunc = getattr(self.target, controlName)
        callback = GenericMsgCallback( callbackFunc, passMsgType=passMsgType, passMsgArgs=passMsgArgs, extraArgs=extraArgs)
        self.inputMap[msgType] = callback

    def mapMsgTypeToCallback(self, msgType, callbackFunc, passMsgType = False, passMsgArgs = True, extraArgs=None):
        callback = GenericMsgCallback( callbackFunc, passMsgType=passMsgType, passMsgArgs=passMsgArgs, extraArgs=extraArgs)
        self.inputMap[msgType] = callback
        
    def processInput(self, msgType, argList):
        try:
            #print "processInput:", msgType, argList
            if msgType in self.inputMap:
                self.inputMap[msgType].call(msgType,argList)
                # self.target.setPos( argList[0], argList[1] )
        except:
            traceback.print_exc()

