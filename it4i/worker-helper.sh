#!/bin/bash

source /etc/profile
source ~/.bashrc

workon pypy

dworker --nthreads=1 --nprocs=24 $@ &
