#!/usr/bin/bash

CRONTAB_DIR="/home/workspace/notebooks/kg_building"
CURRENT_KG=$1
CURRENT_DATASET=$2

SPEC_KG_RELNAME="$CURRENT_DATASET/$CURRENT_KG"

bash $CRONTAB_DIR/build_graph.sh $SPEC_KG_RELNAME >> $CRONTAB_DIR/crontab_log.txt 2>&1