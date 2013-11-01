#!/bin/bash

for i in 1 2 3 4 5 6 7 8 ; do
    #echo "Capturing from am-mac$i"
    #ssh am-mac$i /home/eolson/am-macs/src/flPy/flTile/scripts/tom/do_capture.sh
    ssh am-mac$i /home/eolson/am-macs/src/flPy/flTile/scripts/tom/do_capture.sh &
done
sleep 20
/home/eolson/am-macs/src/flPy/flTile/scripts/tom/makeMontage.sh /home/eolson/am-macs/src/flPy/flTile/scripts/tom/captures

