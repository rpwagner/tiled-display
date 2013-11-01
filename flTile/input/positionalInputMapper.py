
# An adapter to make it easier to switch
#  which object (cursor) an input is  moving.

class PositionalInputMapper (InputMapper):
    def __init__(self, target=None):
        self.target = target
        
    def processInput(self, msgType, argList):
        if self.target:
            self.target.setPos( argList[0], argList[1] )

