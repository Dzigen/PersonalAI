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

KNOWLEDGEGRAPH_NAME=gigachatmax_281025_v2prompts # TO CHANGE
DATASET_NAME=rubq_dev # TO CHANGE

# EXP_NAME
declare -A exp_names # TO CHANGE
exp_names[0]="rubq_gigachatmax_weak_naiveretriever(#cbcafd58)(v2.1.1)"
exp_names[1]="rubq_gigachatmax_weak_naiveretriever(#2723ca24)(v2.1.1)"
exp_names[2]="rubq_gigachatmax_weak_naiveretriever(#1664fa76)(v2.1.1)"
exp_names[3]="rubq_gigachatmax_weak_naiveretriever(#3c2af4a8)(v2.1.1)"

declare -A exp_qapipe_kw # TO CHANGE
exp_qapipe_kw[0]="weak"
exp_qapipe_kw[1]="weak"
exp_qapipe_kw[2]="weak"
exp_qapipe_kw[3]="weak"

# QAHYPERP_PARAMS_PATH
declare -A exp_hyperp # TO CHANGE
exp_hyperp[0]="rubq_gigachatmax_weak_naiveretriever(#cbcafd58)(v2.1.1).yaml"
exp_hyperp[1]="rubq_gigachatmax_weak_naiveretriever(#2723ca24)(v2.1.1).yaml"
exp_hyperp[2]="rubq_gigachatmax_weak_naiveretriever(#1664fa76)(v2.1.1).yaml"
exp_hyperp[3]="rubq_gigachatmax_weak_naiveretriever(#3c2af4a8)(v2.1.1).yaml"

EXPDIR_PARAMS_PATH="$CONFIGURE_BASE_DIR/$PREPARED_PARAMS_NAME/rubq_dev.yaml" # TO CHANGE
EVAL_PARAMS_PATH="$EVALUATE_BASE_DIR/$PREPARED_PARAMS_NAME/rubqdev.yaml" # TO CHANGE

# --------------------------------------------------------

for exp_idx in "${!exp_names[@]}";
do
    EXP_NAME="${exp_names[$exp_idx]}"
    echo "$KNOWLEDGEGRAPH_NAME | $DATASET_NAME | $EXP_NAME"

    QAHYPERP_PARAMS_PATH="$CONFIGURE_BASE_DIR/${exp_qapipe_kw[$exp_idx]}/$PREPARED_PARAMS_NAME/$DATASET_NAME/$KNOWLEDGEGRAPH_NAME/${exp_hyperp[$exp_idx]}"
    echo "qahyperp params-path: $QAHYPERP_PARAMS_PATH"
    echo "expdir params-path: $EXPDIR_PARAMS_PATH"
    echo "eval params-path: $EVAL_PARAMS_PATH"

    bash $EXP_BASE_DIR/run_experiment.sh $KNOWLEDGEGRAPH_NAME $DATASET_NAME $EXP_NAME $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH $EVAL_PARAMS_PATH  >> $RUNEXP_LOG_PATH 2>&1
done

echo "=== Done (run_all_experiments.sh) ==="
