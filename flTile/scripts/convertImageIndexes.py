#!/usr/bin/env python

import sys
from chopImagesIntoTiles import ChangeFilenameIndexesToXY

path=sys.argv[1]
tileXSize=int(sys.argv[2])
ChangeFilenameIndexesToXY(path, tileXSize)

