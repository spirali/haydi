#!/bin/bash

PROJECT_PATH=~/projects/haydi
PROJECT_PATH=$(cd ${PROJECT_PATH}; pwd)

source ${PROJECT_PATH}/it4i/env_init.sh

SRC_DIR=`dirname $0`/../src
PBS_O_WORKDIR=$1
export PYTHONPATH=${PBS_O_WORKDIR}:${SRC_DIR}:${PYTHONPATH}

workon pypy

dask-worker --nthreads=1 $2 $3 &
