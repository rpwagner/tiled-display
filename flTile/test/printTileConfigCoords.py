import os, sys
sys.path = [os.path.join(os.getcwd(), "..") ] + sys.path
sys.path = [os.path.join(os.getcwd(), "..", "..") ] + sys.path

from flTile.amConfig import CreateAMConfig

def run():
    tileConfig = CreateAMConfig()

    #hostname = gethostname()
    #machineDesc = tileConfig.getMachineDescByHostname(hostname)

    print "Machine, local rects, absolute rects"
    for machineDesc in tileConfig.machines:
 
        localRects = []
        absoluteRects = []
        for tile in machineDesc.tiles:
            localRects.append(tileConfig.getLocalDrawRect(tile.uid))
            absoluteRects.append(tileConfig.getAbsoluteFullDisplayRect(tile.uid))

        print machineDesc.hostname, localRects, absoluteRects

    fullRect = tileConfig.getMainDisplayRect()

    print "FULL DISPLAY:", fullRect.width, fullRect.height

if __name__ == "__main__":
    run()

