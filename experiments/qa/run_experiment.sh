#!/usr/bin/bash

EXP_BASE_DIR=/home/workspace/experiments/qa
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
EXP_NAME=$3

QAHYPERP_PARAMS_PATH=$4
EXPDIR_PARAMS_PATH=$5
EVAL_PARAMS_PATH=$6

echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | $EXP_NAME"
echo "qahyperp params-path: $QAHYPERP_PARAMS_PATH"
echo "expdir params-path: $EXPDIR_PARAMS_PATH"
echo "eval params-path: $EVAL_PARAMS_PATH"

# --------------------------------------------------------

CONFIGURE_SCRIPT="$EXP_BASE_DIR/configure/init_exp_environment.sh"
GENERATE_SCRIPT="$EXP_BASE_DIR/generate/generate.sh"
EVALUATE_SCRIPT="$EXP_BASE_DIR/evaluate/evaluate.sh"

# --------------------------------------------------------

bash $CONFIGURE_SCRIPT $EXPDIR_PARAMS_PATH $QAHYPERP_PARAMS_PATH

bash $GENERATE_SCRIPT $EXPDIR_PARAMS_PATH $QAHYPERP_PARAMS_PATH $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME

bash $EVALUATE_SCRIPT $EXPDIR_PARAMS_PATH $QAHYPERP_PARAMS_PATH $EVAL_PARAMS_PATH $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME

echo "=== Done (run_experiment.sh) ==="
