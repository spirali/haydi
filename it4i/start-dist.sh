#!/bin/bash

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
  ssh ${server} -- ${SPATH}/worker-helper.sh ${MASTER} ${WORKER_ARGS} &
done
