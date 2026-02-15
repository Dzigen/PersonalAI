#!/usr/bin/bash
echo "Запуск одного эксперимента по оценке качества построенного графа с заданными параметрами"

BASE_DIR=/home/workspace/experiments/analogues_eval/kg_eval/mine
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

METHOD_NAME=$1
DATASET_NAME=$2
KNOWLEDGEGRAPH_NAME=$3
EXP_NAME=$4

KGEVALHYPERP_PARAMS_PATH=$5
EXPDIR_PARAMS_PATH=$6
EVAL_PARAMS_PATH=$7

echo "$METHOD_NAME | $DATASET_NAME | $KNOWLEDGEGRAPH_NAME | $EXP_NAME"
echo "kgevalhyperp params-path: $KGEVALHYPERP_PARAMS_PATH"
echo "expdir params-path: $EXPDIR_PARAMS_PATH"
echo "eval params-path: $EVAL_PARAMS_PATH"

# --------------------------------------------------------

CONFIGURE_SCRIPT="$BASE_DIR/configure/init_exp_environment.sh"
GENERATE_SCRIPT="$BASE_DIR/perform/perform.sh"
EVALUATE_SCRIPT="$BASE_DIR/evaluate/evaluate.sh"
ANALYZE_SCRIPT="$BASE_DIR/analyze/analyze.sh"
COLLECT_SCRIPT="$BASE_DIR/collect/collect.sh"

# --------------------------------------------------------

bash $CONFIGURE_SCRIPT $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $GENERATE_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $EVALUATE_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH

bash $ANALYZE_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $COLLECT_SCRIPT $METHOD_NAME $DATASET_NAME $KNOWLEDGEGRAPH_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

echo "=== Done (run_experiment.sh) ==="
