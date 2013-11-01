#!/usr/bin/env python

# This script chops up (a sequence of) large images into tiles.

import os, sys, shutil, glob, time, math
from subprocess import Popen, PIPE, STDOUT


if os.path.exists("/home/insley/SOFT/IM_NEW/INSTALL/bin/convert"):
    convert_exec = "/home/insley/SOFT/IM_NEW/INSTALL/bin/convert"
else:
    convert_exec = "convert"


ImageMagickRequiredVersion = "6.4.8-4"
         # filename:tile replacement works in this version

def CheckImageMagickVersion():
    output = Popen(["convert", "--version"], stdout=PIPE).communicate()[0]
    words = output.split()
    versionStr = words[2]
    version = versionStr.split(".")

    testVersion = ImageMagickRequiredVersion.split(".")

    ok = False
    if version[0] > testVersion[0]:
        ok = True
    elif version[0] == testVersion[0]:
        if version[1] > testVersion[1]:
            ok = True
        elif version[1] == testVersion[1]:
            if version[2] >= testVersion[2]:
                ok = True

    return ok


def GetImageSize(path):
    print "GetImageSize:", path
    output = Popen(["identify", path], stdout=PIPE).communicate()[0]
    print "output:", output
    sizeStr = output.split()[2]
    imageSize = sizeStr.split("x")
    imageSize = int(imageSize[0]), int(imageSize[1])
    return imageSize


def ChangeFilenameIndexesToXY(path, tileCols):
    srcFiles2 = os.listdir(path)
    pngSrcFiles2 = []
    for f in srcFiles2:
        #if f.lower().endswith(".png"):
        if os.path.splitext(f.lower())[1] in [".png", ".jpg"]:
            pngSrcFiles2.append(f)

    pngSrcFiles2.sort()
    
    for f in pngSrcFiles2:
        rootname, ext = os.path.splitext(f)
        index = int(rootname.split("_")[-1])
        rootnameWithoutIndex="_".join(rootname.split("_")[:-1])
        x,y = index % tileCols, index / tileCols
        tileDir = os.path.join(path, ("%s_%s") % (x,y))
        if not os.path.exists(tileDir):
            os.mkdir(tileDir)
        origPath = os.path.join(path, f)
        newPath = os.path.join(tileDir, rootnameWithoutIndex + ext)
        ##print "move ", origPath, newPath
	sys.stdout.flush()
        try:
            shutil.move(origPath, newPath)
        except IOError, (errno, strerror):
                ##print "************* IOError: ", errno, ": ", strerror
            if errno != 2:
                print "Unexpected error!!"
                raise
                
def GetMovieDuration(path):
    output = Popen(["ffmpeg", "-i", path], stdout=PIPE, stderr=STDOUT).communicate()[0]
    start = output.index("Duration: ")
    end = output.index(", start: ")
    duration = output[start+len("Duration: "):end]
    hours, mins,secs = duration.split(":")
    totalSecs = float(hours)* 60 * 60 + float(mins) * 60 + float(secs)
    return totalSecs

def GetMovieFPS(path):
    #mplayer -vo null -nosound 0_0.mpg -ss 00:10:00 -endpos 00:00:01
    output = Popen(["mplayer", "-vo", "null", "-nosound", path, "-endpos", "00:00:01"], stdout=PIPE, stderr=STDOUT).communicate()[0]
    linestart = output.index("VIDEO: ")
    lineend = linestart + output[linestart:].index("\n")
    #print "line start,end:", linestart, lineend
    line = output[linestart:lineend]
    #print "line:", line
    words = line.split()
    #print "words:", words
    fpsIndex = words.index("fps") - 1 
    fps = float(words[fpsIndex])
    return fps

def WriteDescription(moviedir, tileDims, largeImageSize, tileRes):
    # Write description
    outfile = os.path.join(moviedir, "description.txt")
    print "Writing description:", outfile
    fd = open(outfile, "w")
    fd.write("Tiles: %sx%s\n" % tileDims)
    fd.write("FullRes: %sx%s\n" % largeImageSize)
    fd.write("TileRes: %sx%s\n" % tileRes)

def AppendDurationToDescription(moviedir):
    # Requires a movie to be generated
    # Find a movie file to get duration from
    movieFiles = os.listdir(moviedir)
    aMovieFile=""
    for file in movieFiles:
        path = os.path.join(moviedir, file)
        if os.path.exists(path) and not os.path.isdir(path):
            aMovieFile = path
            break

    if len(aMovieFile):
        fd = open(os.path.join(moviedir, "description.txt"), "a")
        duration = GetMovieDuration(aMovieFile)
        fd.write("Duration: %s\n" % duration )
    else:
        raise Exception("Could not get duration, movie file not found.")

def AppendFPSToDescription(moviedir):
    # Requires a movie to be generated
    # Find a movie file to get duration from
    movieFiles = os.listdir(moviedir)
    aMovieFile=""
    for file in movieFiles:
        path = os.path.join(moviedir, file)
        if os.path.exists(path) and not os.path.isdir(path):
            aMovieFile = path
            break

    if len(aMovieFile):
        fd = open(os.path.join(moviedir, "description.txt"), "a")
        fps = GetMovieFPS(aMovieFile)
        fd.write("FPS: %s\n" % fps)
    else:
        raise Exception("Could not get FPS, movie file not found.")



##if __name__ == "__main__":

def main():
    global num_procs
    global proc_id
    global tmpdir
    global convert_exec

    num_procs = os.getenv("PMI_SIZE")
    proc_id = os.getenv("PMI_RANK")
        
    if num_procs == None:
	    num_procs = 1
	    proc_id = 0
    else:
	    num_procs = int(num_procs)
	    proc_id = int(proc_id)

    print "num_procs: ", num_procs, "  proc_id: ", proc_id
    sys.stdout.flush()

    #quit()

    #if not CheckImageMagickVersion():
    #    print "ImageMagickVersion of at least %s required." % ImageMagickRequiredVersion

    if len(sys.argv) < 4:
        print "Usage: chopImagesToImageTiles <srcdir> <dstdir> <tileSizeXxY>"
        sys.exit()

    srcdir=sys.argv[1]
    dstdir=sys.argv[2]

    if not os.path.exists(dstdir):
        if proc_id == 0:
            try:
	        os.makedirs(dstdir)
		print "Made directory: ", dstdir
		sys.stdout.flush()
            except OSError, (errno, strerror):
                ##print "OSError: ", errno, ": ", strerror
                if errno != 17:
			print "Unexpected error!!"
			raise
	else:
	    time.sleep(5)

##    if not os.path.exists(dstdir):
##        os.mkdir(dstdir)

    tileSize= sys.argv[3]
    tileXSize,tileYSize = tileSize.split("x")
    tileXSize, tileYSize = int(tileXSize), int(tileYSize)


    srcFiles = os.listdir(srcdir)
    pngSrcFiles = []
    for f in srcFiles:
        #if f.lower().endswith(".png"):
        if os.path.splitext(f.lower())[1] in [".png", ".jpg"]:
            pngSrcFiles.append(f)

    if len(sys.argv) > 4:
	    tempdir = sys.argv[4]
	    try:
		os.makedirs(tempdir)
		print "Made directory: ", dstdir
	    except OSError, (errno, strerror):
                ##print "OSError: ", errno, ": ", strerror
		if errno != 17:
		    print "Unexpected error!!"
		    raise
    else:
	    tempdir = "./"

    print "tempdir: ", tempdir

    ##quit();

    largeImageSize = GetImageSize(os.path.join(srcdir, pngSrcFiles[0]))
    tileCols = float(largeImageSize[0]) / tileXSize
    tileRows = float(largeImageSize[1]) / tileYSize
    # Round fraction of a row up.
    tileCols = int(math.ceil(tileCols))
    tileRows = int(math.ceil(tileRows))

    print "tileCols: ", tileCols, "  tileRows: ", tileRows
    for tileX in range(tileCols):
        for tileY in range(tileRows):
            tileDir = os.path.join(dstdir, ("%s_%s") % (tileX,tileY))
	    if proc_id == 0:
                if not os.path.exists(tileDir):
                    print "Make dir: ", tileDir
                    os.mkdir(tileDir)
	    else:
                if not os.path.exists(tileDir):
                    time.sleep(5)

    ##sys.exit()

    
    if proc_id == 0:
	    WriteDescription(dstdir, tileDims=(tileCols, tileRows), largeImageSize=largeImageSize, tileRes=(tileXSize, tileYSize) )

    if "--description" in sys.argv: # only write description
        sys.exit()

    #for f in pngSrcFiles[:30]: # debug
    filenamesToFix = []

    pngSrcFiles.sort()

    start_index = proc_id
    my_inc = num_procs

#    for f in pngSrcFiles:
    for index in range(start_index, len(pngSrcFiles), my_inc):
	f = pngSrcFiles[index]
        fRoot, fExt = os.path.splitext(f)
        #outfilename = "%s_%s.png" % (os.path.join(dstdir, f.replace(".png", "")), "%d" )
        outfilename = "%s_%s.png" % (os.path.join(dstdir, fRoot), "%d" )
        cmd = "%s %s +gravity -crop %sx%s -depth 8 +repage %s" % (convert_exec, os.path.join(srcdir,f), tileXSize,tileYSize, outfilename)
        ##cmd = "convert %s +gravity -crop %sx%s -depth 8 +repage %s" % (os.path.join(srcdir,f), tileXSize,tileYSize, outfilename)

        
        # slightly more complicated to include row and column indexes in name
        # from: http://www.imagemagick.org/Usage/crop
        #cmd = 'convert %s +gravity -crop %sx%s ' % (os.path.join(srcdir,f), tileXSize,tileYSize) + \
        #      '-set filename:tile "%%[fx:page.x/%d]_%%[fx:page.y/%d]" ' % (tileXSize,tileYSize) + \
        #      ' +repage %s_%%[filename:tile].png' % (os.path.join(dstdir, f.replace(".png", "")) )
        print cmd
        os.system(cmd)
        #filenamesToFix.append(outfilename)
        #if len(filenamesToFix) > 10:
            # Since the -set filename:tile requires a newer imagemagick, do it manually:
        ChangeFilenameIndexesToXY(dstdir, tileCols)
        #    filenamesToFix = []
         
    # one more time:
    ChangeFilenameIndexesToXY(dstdir, tileCols)

    ##  perform synchronization if running in parallel

    if(num_procs > 1):
	my_tmp_name = "chop_proc_" + str(proc_id)
	temp_file = os.path.join(tempdir, my_tmp_name)
	print "proc_id: ", proc_id, "  temp_file: ", temp_file
        ## make a directory with my ID in it
	os.mkdir(temp_file)

        ##print "checking for all to finish"
        ##sys.stdout.flush()
    
	allDone = False
	while not allDone:
            ##print "While not done: checking for all to finish"
            ##sys.stdout.flush()
        
            ##names = os.listdir(tempdir)
	    names = glob.glob(tempdir+"/chop_proc_*")
            ##print node_id, " len(names): ", len(names), "  num_nodes: ", num_nodes
            ##sys.stdout.flush()
	    if(len(names) == int(num_procs)):
		allDone = True
		print "[PROC: ", proc_id, "]:  len(names): ", len(names), "   - can EXIT"
            else:
		time.sleep(10)



    """
    # Prepare to move files.  Get a list of the pngs.
    outFiles = os.listdir(dstdir)
    pngOutFiles = []
    for f in outFiles:
        if f.lower().endswith(".png"):
            pngOutFiles.append(f)

    # Move files into a directory for each tile.
    for f in pngOutFiles:
        tileIndexes=f.split(".")[-2].split("_")[-2:]  # extract X,Y from nnn_X_Y.png
        tileDir="%s_%s" % (tileIndexes[0], tileIndexes[1])
        fullTileDir = os.path.join(dstdir, tileDir)
        if not os.path.exists(fullTileDir):
            print "Making directory:", fullTileDir
            os.mkdir(fullTileDir)
        srcPath = os.path.join(dstdir,f)
        simpleFilename = f.split(".")[-2].split("_")[:-2]    # remove "_X_Y"
        # print "***", f, simpleFilename
        simpleFilename = "_".join(simpleFilename)  + ".png"
        dstPath = os.path.join(dstdir, tileDir, simpleFilename)
        print "Moving from %s to %s." % (srcPath, dstPath)
        shutil.move(srcPath, dstPath)
    """

# Execute the main() function
if __name__ == "__main__":
   main()
