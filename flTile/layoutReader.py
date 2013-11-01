import os, sys

class LayoutObject:
    # FIXME use standard rect-like arg
    def __init__(self, path, pos, size, properties=None):
        self.path = path
        self.pos = pos
        self.size=size
        if properties != None:
            self.properties = dict(properties)
        else:
            self.properties = None

    def getWidth(self):
        return self.size[0]

    def getHeight(self):
        return self.size[1]

    def getProperty(self, name):
        try:
            return self.properties[name]
        except KeyError:
            return None

def ReadLayout(filename):
    contents = open(filename, "r").read()

    lines = contents.split("\n")

    descriptions = []
    # FIXME, read properties from file
    #properties = {"fps":25.0, "duration":30.0}
    properties = {}
    size = None # should be parsed before entries, "example: Size: 256x256"
    for line in lines:
        if len(line.strip()) > 0:
            words = line.split()
            colonSplitWords = line.split(":")
            if 2 == len(colonSplitWords): # property
                colonSplitWords = line.split(":")
                if 2 == len(colonSplitWords):
                    key,value = colonSplitWords
                    key = key.strip().lower()
                    value = value.strip().lower()
                    if key == "size":
                        value = value.split("x")
                        value = [int(i) for i in value] # convert to integers
                        size = value
                        print "Parsed size", size
                    else: # parse generic single value
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    properties[key] = value
                    print "Parse key, value: ", key, value
            elif 3 == len(words):  # regular entry: path x y
                path, xoffset, yoffset = words
                xoffset = int(xoffset)
                yoffset = int(yoffset)
                if None == size:
                    raise Exception( "Layout file should have a size entry. e.g. \"Size: 256x256\"")
                layoutObj = LayoutObject(path, (xoffset, yoffset), size=size, properties=properties)
                descriptions.append( layoutObj )
            else:
                print "skipping line (num parts is not 3): ", line
    return descriptions

if __name__ == "__main__":
    filename = sys.argv[1]
    print ReadLayout(filename)

