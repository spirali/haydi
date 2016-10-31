#!/bin/sh

#PBS -lselect=4:ncpus=24,walltime=01:00:00
#PBS -q qexp
#XPBS -A IT4I-8-2
#PBS -N haydi-test

source /etc/profile

module load Python/2.7.9-GNU-5.1.0-2.25
export PATH=~/.local/bin:$PATH
source ~/.local/bin/virtualenvwrapper.sh

~/projects/pyqit/it4i/start-dist.sh
cd $PBS_O_WORKDIR
sleep 6
workon pypy
time python eqlevel.py --scheduler=127.0.0.1 --port=9010
