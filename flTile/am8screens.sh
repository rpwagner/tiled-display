#!/bin/sh
mpirun -np 4 -machinefile /home/eolson/am-macs/machinefile1234 /home/eolson/am-macs/local/bin/pyMPI tileImage.py -c am8screens $*
