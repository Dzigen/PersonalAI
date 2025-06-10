#!/usr/bin/bash

declare -A exp_names
exp_names[8]="m_v2_llama318b(e5.6.1)(v1.5.5)"
exp_names[12]="nr_v2_llama318b(e5.7.1)(v1.5.5)"

declare -A param_names
param_names[8]="e5.6.1.yaml"
param_names[12]="e5.7.1.yaml"

for exp_idx in "${!exp_names[@]}";
do
    CRONTAB_DIR=/home/workspace/experiments
    DATASET_NAME=trivia_qa_rcwikipedia_validation
    MODEL_NAME=llama318b
    echo "${param_names[$exp_idx]} | ${exp_names[$exp_idx]}"

    bash $CRONTAB_DIR/run_experiment.sh $MODEL_NAME "${param_names[$exp_idx]}" "${exp_names[$exp_idx]}" $DATASET_NAME >> qa_log.txt 2>&1
done
