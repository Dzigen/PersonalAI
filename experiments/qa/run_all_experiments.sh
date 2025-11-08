#!/usr/bin/bash
# Запуск набора экспериментов

EXP_BASE_DIR=/home/workspace/experiments/qa
PYTHON_CMD=/usr/bin/python3
PREPARED_PARAMS_NAME=prepared_params

# --------------------------------------------------------

RUNEXP_LOG_PATH="$EXP_BASE_DIR/runexperiment_log.txt"
CONFIGURE_BASE_DIR="$EXP_BASE_DIR/configure"
EVALUATE_BASE_DIR="$EXP_BASE_DIR/evaluate"

# --------------------------------------------------------

KNOWLEDGEGRAPH_NAME=deepseek_231025_v2prompts # TO CHANGE
DATASET_NAME=hotpotqa_distractor_validation # TO CHANGE
QAPIPELINE_KW="weak" # TO CHANGE

# EXP_NAME
declare -A exp_names # TO CHANGE
exp_names[0]="weak_bs_deepseek(e1)(v2.1.0)"

# QAHYPERP_PARAMS_PATH
declare -A exp_hyperp # TO CHANGE
exp_hyperp[0]="exp1.yaml"

EXPDIR_PARAMS_PATH="$CONFIGURE_BASE_DIR/$PREPARED_PARAMS_NAME/hotpotqa_distractor_validation.yaml" # TO CHANGE

EVAL_PARAMS_PATH="$EVALUATE_BASE_DIR/eval_params.yaml" # TO CHANGE

# --------------------------------------------------------

for exp_idx in "${!exp_names[@]}";
do
    EXP_NAME="${exp_names[$exp_idx]}"
    echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | $EXP_NAME"

    QAHYPERP_PARAMS_PATH="$CONFIGURE_BASE_DIR/$QAPIPELINE_KW/$PREPARED_PARAMS_NAME/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME"
    echo "qahyperp params-path: $QAHYPERP_PARAMS_PATH"
    echo "expdir params-path: $EXPDIR_PARAMS_PATH"
    echo "eval params-path: $EVAL_PARAMS_PATH"

    bash $EXP_BASE_DIR/run_experiment.sh $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH  >> $RUNEXP_LOG_PATH 2>&1
done

echo "=== Done (run_all_experiments.sh) ==="
