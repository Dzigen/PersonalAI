#!/usr/bin/bash
echo "Оценка качества сгенерированных ответов в рамках заданного QA-эксперимента"

EXP_BASE_DIR=/home/workspace/experiments/analogues_eval/qa_eval
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

METHOD_NAME=$1
DATASET_NAME=$2
KNOWLEDGEGRAPH_NAME=$3
EXP_NAME=$4

QAHYPERP_PARAMS_PATH=$5
EXPDIR_PARAMS_PATH=$6
EVAL_PARAMS_PATH=$7

# --------------------------------------------------------

BASE_RESULTS_DIR="$EXP_BASE_DIR/results"
CUR_EXP_BASE_DIR="$BASE_RESULTS_DIR/$METHOD_NAME/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
SPEC_EXP_DIR="$CUR_EXP_BASE_DIR/$EXP_NAME"

BASE_EVALUATE_DIR="$EXP_BASE_DIR/evaluate"

# --------------------------------------------------------

BASE_EVALUATE_SCRIPT="$BASE_EVALUATE_DIR/evaluate_answers.py"
LLMASJUDGE_EVALUATE_SCRIPT="$BASE_EVALUATE_DIR/evaluate_llmjudge.py"

BASEEVALUATE_LOG_PATH="$SPEC_EXP_DIR/baseeval_log.txt"
LLMASJUDGEEVALUATE_LOG_PATH="$SPEC_EXP_DIR/llmasajudgeeval_log.txt"

# --------------------------------------------------------

ACCUMULATE_SCORES_SCRIPT="$BASE_EVALUATE_DIR/accumulate_packs_scores.py"

ACCUMULATESCORES_LOG_PATH="$SPEC_EXP_DIR/accumulatescores_log.txt"

# --------------------------------------------------------

echo $SPEC_EXP_DIR
echo $BASEEVALUATE_LOG_PATH
echo $LLMASJUDGEEVALUATE_LOG_PATH
echo $ACCUMULATESCORES_LOG_PATH

cd $SPEC_EXP_DIR ; $PYTHON_CMD $BASE_EVALUATE_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH >> $BASEEVALUATE_LOG_PATH 2>&1

cd $SPEC_EXP_DIR ; $PYTHON_CMD $LLMASJUDGE_EVALUATE_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH >> $LLMASJUDGEEVALUATE_LOG_PATH 2>&1

cd $SPEC_EXP_DIR ; $PYTHON_CMD $ACCUMULATE_SCORES_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $ACCUMULATESCORES_LOG_PATH 2>&1

echo "=== Done (evaluate.sh) ==="
