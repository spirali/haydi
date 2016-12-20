#!/bin/bash

PROJECT_PATH=~/projects/haydi
PROJECT_PATH=$(cd ${PROJECT_PATH}; pwd)

source ${PROJECT_PATH}/it4i/env_init.sh

workon pypy

python ${PROJECT_PATH}/it4i/qsub_run.py ${HAYDI_ARGS}