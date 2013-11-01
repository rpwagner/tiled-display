#!/bin/bash

movieFile=$1
workDir=$2
framesDir=$workDir/frames
tilesDir=$workDir/tiles
tiledMovieDir=$workDir/movie.tdmovie
scriptsDir=~eolson/am-macs/src/flPy/flTile/scripts

. ~eolson/am-macs/env.sh
cd ~eolson/am-macs/src/flPy/flTile/scripts

echo "Converting movie to frames"
mkdir -p $framesDir
python $scriptsDir/movieToImages.py $movieFile $framesDir
if [ "$?" != "0" ] ; then
  echo "exiting with error $?"
  exit
fi

echo "Resizing"
echo mogrify -resize 5120x2304 $framesDir/\*.png 
mogrify -resize 5120x2304 $framesDir/*.png

echo "Cutting frames into tiles"
mkdir -p $tilesDir
echo python $scriptsDir/chopImagesToImageTiles.py $framesDir $tilesDir 128x128  
python $scriptsDir/chopImagesToImageTiles.py $framesDir $tilesDir 128x128
if [ "$?" != "0" ] ; then
  echo "exiting with error $?"
  exit
fi

echo "Compositing tiles into movies"
# mkdir -p $tiledMovieDir
echo python $scriptsDir/imageTilesToTiledMovie.py $tilesDir $tiledMovieDir
python $scriptsDir/imageTilesToTiledMovie.py $tilesDir $tiledMovieDir
if [ "$?" != "0" ] ; then
  echo "exiting with error $?"
  exit
fi

echo "Copying tiled movies to all machines"
#python ~eolson/am-macs/scripts/run.py "mkdir -p $tiledMovieDir"
#python ~eolson/am-macs/scripts/run.py "scp -r am-mac2:$tiledMovieDir $tiledMovieDir"
if [ "$?" != "0" ] ; then
  echo "exiting with error $?"
  exit
fi

echo "Finished"

