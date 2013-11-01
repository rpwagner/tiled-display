dir=$1
#echo "Joining 123"
montage $dir/screen.am-mac[1,2,3,4].mcs.anl.gov.png -gravity North -tile 1x -geometry +0+0 $dir/1234.png
#echo "Joining 456"
montage $dir/screen.am-mac[5,6,7,8].mcs.anl.gov.png -gravity North -tile 1x -geometry +0+0 $dir/5678.png
#echo "Joining 123 and 456"
#montage $dir/123.png $dir/456.png  -tile x1 -geometry +0+0 $dir/123456.png
#echo "Joining 78"
#montage $dir/screen.am-mac[78].mcs.anl.gov.png -tile 1x -gravity North -geometry +0+0 $dir/78.png
#echo "Joining 123456 and 78"
outfile=$dir/am-`date +"%Y-%m-%d-%H%M%S"`.png
#latest=$dir/am.png
latest=$HOME/am.png
latest_small=$dir/am-small.png
latest_medium=$dir/am-medium.png
#montage $dir/123456.png $dir/78.png -tile x1 -gravity North -geometry +0+0 -size 1280x576 $outfile
#montage $dir/123.png $dir/456.png -tile x1 -gravity North -geometry +0+0 -size 1280x576 $outfile
montage $dir/1234.png $dir/5678.png -tile x1 -gravity North -geometry +0+0 -size 1024x1024 $outfile
cp $outfile $latest
#convert $latest -thumbnail '1024x460' $latest_medium
convert $latest -thumbnail '768x768' $latest_medium
#convert $latest -thumbnail '512x230' $latest_small
convert $latest -thumbnail '512x512' $latest_small
date +%s > $dir/am.time
