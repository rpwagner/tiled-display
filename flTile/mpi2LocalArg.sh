#!/bin/sh
export TD_HOSTNAMES=maze,maze2
mpirun -np 2 /usr/local/bin/pyMPI tileImage.py -c local2_1680x1050Config $*
