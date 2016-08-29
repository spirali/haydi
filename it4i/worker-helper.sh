#!/bin/bash

source /etc/profile

module load Python/2.7.9-GNU-5.1.0-2.25
export PATH=~/.local/bin:$PATH
source ~/.local/bin/virtualenvwrapper.sh

SRC_DIR=`dirname $0`/../src
PBS_O_WORKDIR=$1
export PYTHONPATH=$PBS_O_WORKDIR:$SRC_DIR:$PYTHONPATH

workon pypy

dworker --nthreads=1 --nprocs=24 $2 $3 &
