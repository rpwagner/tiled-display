import sys
from chopImagesToImageTiles import GetMovieDuration
duration = GetMovieDuration(sys.argv[1])
print "Duration:", duration
