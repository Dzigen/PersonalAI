#!/usr/bin/bash
echo "Запуск одного эксперимента по оценке качества построенного графа с заданными параметрами"

EXP_BASE_DIR=/home/workspace/experiments/kg_eval/mine
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
EXP_NAME=$3

KGEVALHYPERP_PARAMS_PATH=$4
EXPDIR_PARAMS_PATH=$5
EVAL_PARAMS_PATH=$6

echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | $EXP_NAME"
echo "kgevalhyperp params-path: $KGEVALHYPERP_PARAMS_PATH"
echo "expdir params-path: $EXPDIR_PARAMS_PATH"
echo "eval params-path: $EVAL_PARAMS_PATH"

# --------------------------------------------------------

CONFIGURE_SCRIPT="$EXP_BASE_DIR/configure/init_exp_environment.sh"
GENERATE_SCRIPT="$EXP_BASE_DIR/perform/perform.sh"
EVALUATE_SCRIPT="$EXP_BASE_DIR/evaluate/evaluate.sh"
ANALYZE_SCRIPT="$EXP_BASE_DIR/analyze/analyze.sh"
COLLECT_SCRIPT="$EXP_BASE_DIR/collect/collect.sh"

# --------------------------------------------------------

bash $CONFIGURE_SCRIPT $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $GENERATE_SCRIPT $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $EVALUATE_SCRIPT $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH

bash $ANALYZE_SCRIPT $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

bash $COLLECT_SCRIPT $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $KGEVALHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH

echo "=== Done (run_experiment.sh) ==="
