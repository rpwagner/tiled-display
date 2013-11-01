
class VisualsManager:

    # Responsible for creating new visual objects.
    #  (later might hold a layout manager responsible for layout as well)

    def __init__(self):
        self.renderers = []
        self.objectListList = None
        self.cursorListList = None
        self.inUseCursorIndexes = []

    def setRenderers(self, renderers):
        self.renderers = list(renderers) # copy of the list

    def setObjectListListByRef(self, oll):
        self.objectListList = oll

    def setMasterObjectListByRef(self, mObjs):
        self.masterObjectList = mObjs

    def setCursorListList_tmpFunc(self, cll):
        # FIXME: cursors should be created from within this class and added to
        #     the state when needed.
        self.cursorListList = cll

    def setupNewVisualRepresentation(self):
        # currently return one of 4 preloaded icons
        # later fix to add new obj during this call.
        for i in range(len(self.cursorListList)):
            if i not in self.inUseCursorIndexes: # select this cursor
                self.inUseCursorIndexes.append(i)
                return self.cursorListList[i][0]
        print "WARNING: setupNewVisualRepresentation(): No more available cursors, make this dynamic."
        return None 

    def releaseVisualRepresentation(self, obj):
        # currently release one of 4 preloaded icons
        # later fix to delete obj during this call.
        for i in range(len(self.cursorListList)):
            if self.cursorListList[i][0] == obj:
                if i in self.inUseCursorIndexes:
                    self.inUseCursorIndexes.remove(i)
                else:
                    print "WARNING: releaseVisualRepresentation() found obj, but it's not in use."
                return
        print "WARNING: releaseVisualRepresentation() found no matching obj."
        

