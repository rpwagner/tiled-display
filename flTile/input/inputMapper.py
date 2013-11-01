
# Base class
# An adapter to make it easier to switch
#  what input data is affecting.
#  For example, which cursor data is moving.

class InputMapper:
    def __init__(self):
        pass

    def processInput(self, msgType, argList):
        print "InputMapper::processInput should be overidden by child class."

