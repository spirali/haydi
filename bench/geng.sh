#!/usr/bin/env bash

NAUTY_PATH=${1}
GENG_PATH=${NAUTY_PATH}/geng
SHOWG_PATH=${NAUTY_PATH}/showg
COUNT=${2-5}

echo "geng"
time -p ${GENG_PATH} -u -q ${COUNT}

echo "geng + manual wrapper"
time -p ${GENG_PATH} -g -q ${COUNT} | ${SHOWG_PATH} -e -q | python ./convert-graph6.py

echo "geng + networkx"
time -p ${GENG_PATH} -g -q ${COUNT} | python ./convert-graph6-networkx.py
