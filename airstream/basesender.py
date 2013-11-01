
class BaseSender:
    def __init__(self):
        self.producingInput = True

    def startInputProduction(self):
        print "Will now produce input"
        self.producingInput = True

    def stopInputProduction(self):
        self.producingInput = False
        print "Will now Not produce input"

