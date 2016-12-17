#!/bin/sh

#PBS -lselect=4:ncpus=24,walltime=01:00:00
#PBS -q qexp
#XPBS -A IT4I-8-2
#PBS -N haydi-test

SERVER="127.0.0.1"
PORT=9020
PROJECT_PATH="~/projects/pyqit"

source /etc/profile

module load Python/2.7.9-GNU-5.1.0-2.25
export PATH=~/.local/bin:$PATH
source ~/.local/bin/virtualenvwrapper.sh

${PROJECT_PATH}/it4i/start-dist.sh

# wait for cluster to start
WORKER_COUNT=$(wc -l < $PBS_NODEFILE)
WORKER_COUNT=$(($WORKER_COUNT * 24))
echo "Waiting for $WORKER_COUNT workers..."

while [ `python ${PROJECT_PATH}/it4i/count_workers.py "$SERVER:$PORT"` -ne ${WORKER_COUNT} ]; do
        sleep 1;
done
echo "Cluster started"

cd ${PBS_O_WORKDIR}

workon pypy
time python eqlevel.py --scheduler=${SERVER} --port=${PORT}
