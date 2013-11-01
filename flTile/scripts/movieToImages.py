#!/usr/bin/env python

# This script takes a movie and saves out the individual frames

import os, sys, shutil, traceback
try:
    import pyffmpeg
except:
    traceback.print_exc()
    print "ERROR: Could not import ffmpeg"
    print "  For movieToImages, try this instead: ffmpeg -i video.mpg image%08d.jpg"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: movieToImages <srcfile> <dstdir>"
        sys.exit()

    srcfile=sys.argv[1]
    dstdir=sys.argv[2]

    stream = pyffmpeg.VideoStream()
    stream.open(srcfile)

    if not os.path.exists(dstdir):
        os.mkdir(dstdir)

    basename=os.path.basename(srcfile)
    if not len(basename):
        basename = "frame"
    basename = os.path.splitext(basename)[0] # remove extension

    frameNum = 0
    while 1:
        try:
            image = stream.GetFrameNo(frameNum)
            outpath = os.path.join(dstdir, "%s_%08d.png" % (basename, frameNum))
            image.save(outpath)
            frameNum += 1
        except IOError:
            print "Couldn't read another frame.  Finished."
            sys.exit()


