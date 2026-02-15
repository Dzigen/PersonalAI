#!/usr/bin/bash
echo "Запуск одного qa-эксперимента с заданными параметрами"

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

echo "$METHOD_NAME | $DATASET_NAME | $KNOWLEDGEGRAPH_NAME | $EXP_NAME"
echo "qahyperp params-path: $QAHYPERP_PARAMS_PATH"
echo "expdir params-path: $EXPDIR_PARAMS_PATH"
echo "eval params-path: $EVAL_PARAMS_PATH"

# --------------------------------------------------------

CONFIGURE_SCRIPT="$EXP_BASE_DIR/configure/init_exp_environment.sh"
GENERATE_SCRIPT="$EXP_BASE_DIR/generate/generate.sh"
EVALUATE_SCRIPT="$EXP_BASE_DIR/evaluate/evaluate.sh"
COLLECT_SCRIPT="$EXP_BASE_DIR/collect/collect.sh"

# --------------------------------------------------------

bash $CONFIGURE_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $GENERATE_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $EVALUATE_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH

bash $COLLECT_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

echo "=== Done (run_experiment.sh) ==="
