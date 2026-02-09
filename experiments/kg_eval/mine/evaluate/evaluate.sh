#!/usr/bin/bash
echo "Оценка качества построенного графа"

EXP_BASE_DIR=/home/workspace/experiments/kg_eval/mine
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
EXP_NAME=$3

KGEVALHYPERP_PARAMS_PATH=$4
EXPDIR_PARAMS_PATH=$5
EVAL_PARAMS_PATH=$6

# --------------------------------------------------------

BASE_RESULTS_DIR="$EXP_BASE_DIR/results"
CUR_EXP_BASE_DIR="$BASE_RESULTS_DIR/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
SPEC_EXP_DIR="$CUR_EXP_BASE_DIR/$EXP_NAME"

BASE_EVALUATE_DIR="$EXP_BASE_DIR/evaluate"

# --------------------------------------------------------

LLMASJUDGE_EVALUATE_SCRIPT="$BASE_EVALUATE_DIR/evaluate_llmjudge.py"

LLMASJUDGEEVALUATE_LOG_PATH="$SPEC_EXP_DIR/llmasajudgeeval_log.txt"

# --------------------------------------------------------

cd $SPEC_EXP_DIR ; $PYTHON_CMD $LLMASJUDGE_EVALUATE_SCRIPT $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH >> $LLMASJUDGEEVALUATE_LOG_PATH 2>&1

cd $SPEC_EXP_DIR ; $PYTHON_CMD $ACCUMULATE_SCORES_SCRIPT $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $ACCUMULATESCORES_LOG_PATH 2>&1

echo "=== Done (evaluate.sh) ==="
