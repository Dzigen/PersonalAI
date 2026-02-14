#!/usr/bin/bash
echo "Извлечение триплтетов, релевантных запросу, из построенного графа"

EXP_BASE_DIR=/home/workspace/kg_eval/mine
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
EXP_NAME=$3

KGEVALHYPERP_PARAMS_PATH=$4
EXPDIR_PARAMS_PATH=$5

# --------------------------------------------------------

BASE_RESULTS_DIR="$EXP_BASE_DIR/results"
CUR_EXP_BASE_DIR="$BASE_RESULTS_DIR/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
SPEC_EXP_DIR="$CUR_EXP_BASE_DIR/$EXP_NAME"

BASE_GENERATE_DIR="$EXP_BASE_DIR/perform"

# --------------------------------------------------------

RETRTRIPLES_SCRIPT="$BASE_GENERATE_DIR/perform.py"

RETRTRIPLES_LOG_PATH="$SPEC_EXP_DIR/retrieving_log.txt"

# --------------------------------------------------------

cd $SPEC_EXP_DIR ; $PYTHON_CMD $RETRTRIPLES_SCRIPT $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $RETRTRIPLES_LOG_PATH 2>&1

echo "=== Done (perform.sh) ==="
