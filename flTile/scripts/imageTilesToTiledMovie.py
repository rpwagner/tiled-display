#!/usr/bin/env python

# This script takes a folder with subfolders of images
#   and creates a movie for each.

from chopImagesToImageTiles import AppendDurationToDescription, AppendFPSToDescription

import os, sys, shutil, glob, time
if len(sys.argv) < 3:
    print "Usage: imageTilesToTiledMovie <srcdir> <dstdir>"
    sys.exit()

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


srcdir=sys.argv[1]
dstdir=sys.argv[2]

if not dstdir.lower().endswith(".tdmovie"):
    dstdir += ".tdmovie"

#if not os.path.exists(dstdir):
#    os.mkdir(dstdir)

print "len(sys.argv): ", len(sys.argv)
print 
#sys.exit()

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


if len(sys.argv) > 3:
    tempdir = sys.argv[3]
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

#sys.exit()

# There should be directories for each tile in srcdir
dirContents = os.listdir(srcdir)
srcDirs = []
for path in dirContents:
    if os.path.isdir(os.path.join(srcdir, path)):
        srcDirs.append(path)
#for d in srcDirs[:1]: # debug

# Determine the filename format:
files = os.listdir(os.path.join(srcdir, srcDirs[0]))
print "files: ", files

filename=files[0]
print "filename: ", filename

basefilename = os.path.splitext(filename)[0]
print "basefilename: ", basefilename
divider = basefilename.rindex(".")  # find the last underscore
basefilename = basefilename[:divider]
print "** basefilename: ", basefilename

start_index = proc_id
my_inc = num_procs


#for d in srcDirs:
for index in range(start_index, len(srcDirs), my_inc):
    d = srcDirs[index]
    fullD = os.path.join(srcdir,d)
    print fullD
    if os.path.isdir(fullD):
        # ffmpeg -sameq -i /tmp/heart/heart_%08d.png  test.mpg
        ##inPath = os.path.join(fullD, basefilename + "_%08d.png")
        inPath = os.path.join(fullD, basefilename + ".%04d.png")
        outPath = os.path.join(dstdir, d + ".mp4")
        cmd = "ffmpeg -sameq -i %s %s" % ( inPath, outPath)
        print cmd
        os.system(cmd)

if proc_id == 0:
    shutil.copy(os.path.join(srcdir, "description.txt"),  dstdir)
    AppendDurationToDescription(dstdir)
    AppendFPSToDescription(dstdir)

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
