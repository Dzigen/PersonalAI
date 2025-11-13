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

# EXP_NAME
declare -A exp_names # TO CHANGE
exp_names[0]="hotpotqa_deepseek_weak_naiveretriever(#f18f0a4c)(v2.1.2)"
exp_names[1]="hotpotqa_deepseek_weak_naiveretriever(#eaf63639)(v2.1.2)"
exp_names[2]="hotpotqa_deepseek_weak_naiveretriever(#d0eec5e5)(v2.1.2)"
exp_names[3]="hotpotqa_deepseek_weak_naiveretriever(#1000a252)(v2.1.2)"
exp_names[4]="hotpotqa_deepseek_weak_naiveretriever(#52c09679)(v2.1.2)"
exp_names[5]="hotpotqa_deepseek_weak_naiveretriever(#8c93a60f)(v2.1.2)"
exp_names[6]="hotpotqa_deepseek_weak_naiveretriever(#5f868ca4)(v2.1.2)"
exp_names[7]="hotpotqa_deepseek_weak_naiveretriever(#3e3e30a8)(v2.1.2)"

declare -A exp_qapipe_kw # TO CHANGE
exp_qapipe_kw[0]="weak"
exp_qapipe_kw[1]="weak"
exp_qapipe_kw[2]="weak"
exp_qapipe_kw[3]="weak"
exp_qapipe_kw[4]="weak"
exp_qapipe_kw[5]="weak"
exp_qapipe_kw[6]="weak"
exp_qapipe_kw[7]="weak"

# QAHYPERP_PARAMS_PATH
declare -A exp_hyperp # TO CHANGE
exp_hyperp[0]="hotpotqa_deepseek_weak_naiveretriever(#f18f0a4c)(v2.1.2).yaml"
exp_hyperp[1]="hotpotqa_deepseek_weak_naiveretriever(#eaf63639)(v2.1.2).yaml"
exp_hyperp[2]="hotpotqa_deepseek_weak_naiveretriever(#d0eec5e5)(v2.1.2).yaml"
exp_hyperp[3]="hotpotqa_deepseek_weak_naiveretriever(#1000a252)(v2.1.2).yaml"
exp_hyperp[4]="hotpotqa_deepseek_weak_naiveretriever(#52c09679)(v2.1.2).yaml"
exp_hyperp[5]="hotpotqa_deepseek_weak_naiveretriever(#8c93a60f)(v2.1.2).yaml"
exp_hyperp[6]="hotpotqa_deepseek_weak_naiveretriever(#5f868ca4)(v2.1.2).yaml"
exp_hyperp[7]="hotpotqa_deepseek_weak_naiveretriever(#3e3e30a8)(v2.1.2).yaml"

EXPDIR_PARAMS_PATH="$CONFIGURE_BASE_DIR/$PREPARED_PARAMS_NAME/hotpotqa_distractor_validation.yaml" # TO CHANGE
EVAL_PARAMS_PATH="$EVALUATE_BASE_DIR/$PREPARED_PARAMS_NAME/hotpotqa.yaml" # TO CHANGE

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
