#!/bin/sh

#PBS -lselect=4:ncpus=24,walltime=00:10:00
#PBS -q qexp
#XPBS -A IT4I-8-2
#PBS -N pyqit-test
module load Python/2.7.9-GNU-5.1.0-2.25
~/projects/pyqit/it4i/start-dist.sh
cd $PBS_O_WORKDIR
python eqlevel_dist.py 127.0.0.1 9010
