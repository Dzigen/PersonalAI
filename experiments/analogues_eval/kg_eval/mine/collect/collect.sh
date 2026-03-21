#!/usr/bin/bash
echo "Отправка полученных результатов в MLFlow для анализа"

EXP_BASE_DIR=/home/workspace/experiments/analogues_eval/kg_eval/mine
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

METHOD_NAME=$1
DATASET_NAME=$2
KNOWLEDGEGRAPH_NAME=$3
EXP_NAME=$4

QAHYPERP_PARAMS_PATH=$5
EXPDIR_PARAMS_PATH=$6

# --------------------------------------------------------

BASE_RESULTS_DIR="$EXP_BASE_DIR/results"
CUR_EXP_BASE_DIR="$BASE_RESULTS_DIR/$METHOD_NAME/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
SPEC_EXP_DIR="$CUR_EXP_BASE_DIR/$EXP_NAME"

BASE_EVALUATE_DIR="$EXP_BASE_DIR/collect"

# --------------------------------------------------------

SENDTOMLFLOW_SCRIPT="$BASE_EVALUATE_DIR/send_to_mlflow.py"

SENDTOMLFLOW_LOG_PATH="$SPEC_EXP_DIR/send_to_mlflow_log.txt"

# --------------------------------------------------------

cd $SPEC_EXP_DIR ; $PYTHON_CMD $SENDTOMLFLOW_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $SENDTOMLFLOW_LOG_PATH 2>&1

echo "=== Done (collect.sh) ==="
