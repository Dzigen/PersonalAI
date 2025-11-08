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
exp_names[0]="m_v2_gpt4omini(e4.4.1)(v1.5.5)"
exp_names[1]="m_v2_gpt4omini(e4.4.2)(v1.5.5)"

# QAHYPERP_PARAMS_PATH
declare -A exp_hyperp # TO CHANGE
exp_hyperp[0]="m_v2_gpt4omini(e4.4.1)(v1.5.5)"
exp_hyperp[1]="m_v2_gpt4omini(e4.4.2)(v1.5.5)"

EXPDIR_PARAMS_PATH="$CONFIGURE_BASE_DIR/$PREPARED_PARAMS_NAME/hotpotqa_distractor_validation.yaml" # TO CHANGE

EVAL_PARAMS_PATH="$EVALUATE_BASE_DIR/eval_params.yaml" # TO CHANGE

# --------------------------------------------------------

for exp_idx in "${!exp_names[@]}";
do
    echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | ${exp_names[$exp_idx]}"
    echo "qahyperp params-path: ${exp_hyperp[$exp_idx]}"
    echo "expdir params-path: $EXPDIR_PARAMS_PATH"
    echo "eval params-path: $EVAL_PARAMS_PATH"

    bash $EXP_BASE_DIR/run_experiment.sh $KNOWLEDGEGRAPH_NAME $DATASET_NAME "${exp_names[$exp_idx]}" "${exp_hyperp[$exp_idx]}" $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH  >> $RUNEXP_LOG_PATH 2>&1
done

echo "=== Done (run_all_experiments.sh) ==="
