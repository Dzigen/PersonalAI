#!/usr/bin/bash
# Запуск набора экспериментов

EXP_BASE_DIR=/home/workspace/experiments/qa
PYTHON_CMD=/usr/bin/python3
PREPARED_PARAMS_NAME=prepared_params

# --------------------------------------------------------

RUNEXP_LOG_PATH="$EXP_BASE_DIR/runexperiment_log.txt"
EVALUATE_BASE_DIR="$EXP_BASE_DIR/evaluate"
PARAMSTORUN_DIR="$EXP_BASE_DIR/params_to_run"
CONFIGURE_BASE_DIR="$EXP_BASE_DIR/configure"

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=$1
DATASET_NAME=$2
CONFIGURE_FNAME=$3
EVAL_FNAME=$4

EXPDIR_PARAMS_PATH="$CONFIGURE_BASE_DIR/$PREPARED_PARAMS_NAME/$CONFIGURE_FNAME"
EVAL_PARAMS_PATH="$EVALUATE_BASE_DIR/$PREPARED_PARAMS_NAME/$EVAL_FNAME"

# --------------------------------------------------------

exp_hyperp=($(ls $PARAMSTORUN_DIR))
for exp_idx in "${!exp_hyperp[@]}";
do  
    HYPERP_FNAME="${exp_hyperp[$exp_idx]}"
    EXP_NAME=${HYPERP_FNAME%.yaml}
    echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | $EXP_NAME"

    QAHYPERP_PARAMS_PATH="$PARAMSTORUN_DIR/$HYPERP_FNAME"
    echo "qahyperp params-path: $QAHYPERP_PARAMS_PATH"
    echo "expdir params-path: $EXPDIR_PARAMS_PATH"
    echo "eval params-path: $EVAL_PARAMS_PATH"

    bash $EXP_BASE_DIR/run_experiment.sh $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH  >> $RUNEXP_LOG_PATH 2>&1
done

echo "=== Done (run_all_experiments.sh) ==="
