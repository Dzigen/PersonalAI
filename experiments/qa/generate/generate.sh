#!/usr/bin/bash
# Запуск QA-пайплайна (генерация ответов на вопросы) в рамках заданной конфигурации

EXP_BASE_DIR=/home/workspace/experiments/qa
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
EXP_NAME=$3

QAHYPERP_PARAMS_PATH=$4
EXPDIR_PARAMS_PATH=$5

# --------------------------------------------------------

BASE_RESULTS_DIR="$EXP_BASE_DIR/results"
CUR_EXP_BASE_DIR="$BASE_RESULTS_DIR/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
SPEC_EXP_DIR="$CUR_EXP_BASE_DIR/$EXP_NAME"

BASE_GENERATE_DIR="$EXP_BASE_DIR/generate"

# --------------------------------------------------------

GENANSW_SCRIPT="$BASE_GENERATE_DIR/generate_answers.py"

GENANSW_LOG_PATH="$SPEC_EXP_DIR/inference_log.txt"

# --------------------------------------------------------

cd $SPEC_EXP_DIR ; $PYTHON_CMD $GENANSW_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $GENANSW_LOG_PATH 2>&1

echo "=== Done (generate.sh) ==="
