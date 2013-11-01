import sys, os
path = sys.argv[1]

from chopImagesToImageTiles import AppendDurationToDescription, AppendFPSToDescription

descriptPath = os.path.join(path, "description.txt")
if not os.path.exists(descriptPath):
    f = open(descriptPath, "w" )
    f.write("\n")
    f.close()

AppendDurationToDescription(path)
AppendFPSToDescription(path)

