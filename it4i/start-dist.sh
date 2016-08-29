#!/bin/bash

# Init

module load Python/2.7.9-GNU-5.1.0-2.25
export PATH=~/.local/bin:$PATH
source ~/.local/bin/virtualenvwrapper.sh

PORT=9010
MASTER=`hostname`:${PORT}

WORKER_ARGS=$@

workon pypy

dscheduler --port ${PORT} &> dscheduler.log &
echo "Pid of scheduler: $!"
echo "Url: ${MASTER}"

sleep 1

SPATH=`dirname $0`
[ $SPATH = '.' ] && SPATH=$PWD

# Start workers
for server in `cat $PBS_NODEFILE` ; do 
  echo Starting client ... ${server}
  ssh ${server} -- ${SPATH}/worker-helper.sh ${PBS_O_WORKDIR} ${MASTER} ${WORKER_ARGS} &
done
