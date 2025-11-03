#!/usr/bin/bash


# BASE_DIR=/home/workspace/experiments
# 14 23 16 05 * bash run_all_experiments.sh >> runall_cron.txt 2>&!

declare -A exp_names
exp_names[0]="m_v2_gpt4omini(e4.4.1)(v1.5.5)"
exp_names[1]="m_v2_gpt4omini(e4.4.2)(v1.5.5)"
exp_names[2]="m_v2_gpt4omini(e4.4.3)(v1.5.5)"
exp_names[3]="m_v2_gpt4omini(e4.4.4)(v1.5.5)"
exp_names[4]="m_v2_gpt4omini(e4.5.2)(v1.5.5)"
exp_names[5]="m_v2_gpt4omini(e4.5.3)(v1.5.5)"
exp_names[6]="m_v2_gpt4omini(e4.5.4)(v1.5.5)"
exp_names[7]="m_v2_gpt4omini(e4.6.2)(v1.5.5)"
exp_names[8]="m_v2_gpt4omini(e4.6.3)(v1.5.5)"
exp_names[9]="m_v2_gpt4omini(e4.6.4)(v1.5.5)"

declare -A param_names
param_names[0]="e4.4.1.yaml"
param_names[1]="e4.4.2.yaml"
param_names[2]="e4.4.3.yaml"
param_names[3]="e4.4.4.yaml"
param_names[4]="e4.5.2.yaml"
param_names[5]="e4.5.3.yaml"
param_names[6]="e4.5.4.yaml"
param_names[7]="e4.6.2.yaml"
param_names[8]="e4.6.3.yaml"
param_names[9]="e4.6.4.yaml"

for exp_idx in "${!exp_names[@]}";
do
    CRONTAB_DIR=/home/workspace/experiments
    DATASET_NAME=trivia_qa_rcwikipedia_validation
    MODEL_NAME=llama318b
    echo "${param_names[$exp_idx]} | ${exp_names[$exp_idx]}"

    bash $CRONTAB_DIR/run_experiment.sh $MODEL_NAME "${param_names[$exp_idx]}" "${exp_names[$exp_idx]}" $DATASET_NAME >> qa_log.txt 2>&1
done
