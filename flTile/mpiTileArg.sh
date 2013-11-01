#!/bin/sh
mpirun -np 8 -machinefile /home/eolson/am-macs/machinefile /home/eolson/am-macs/local/bin/pyMPI tileImage.py $*
