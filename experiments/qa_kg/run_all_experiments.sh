#!/usr/bin/bash

declare -A exp_names
exp_names[0]="wc_v2_gpt4omini(e4.1.1)(v1.5.5)"
exp_names[1]="astar_v2_gpt4omini(e4.2.1)(v1.5.5)"
exp_names[2]="astar_v2_gpt4omini(e4.2.2)(v1.5.5)"
exp_names[3]="astar_v2_gpt4omini(e4.2.3)(v1.5.5)"
exp_names[4]="astar_v2_gpt4omini(e4.2.4)(v1.5.5)"
exp_names[5]="bs_v2_gpt4omini(e4.3.1)(v1.5.5)"
exp_names[6]="bs_v2_gpt4omini(e4.3.2)(v1.5.5)"
exp_names[7]="bs_v2_gpt4omini(e4.3.3)(v1.5.5)"
exp_names[8]="bs_v2_gpt4omini(e4.3.4)(v1.5.5)"
exp_names[9]="nr_v2_gpt4omini(e4.7.1)(v1.5.5)"

declare -A param_names
exp_names[0]="e4.1.1.yaml"
exp_names[1]="e4.2.1.yaml"
exp_names[2]="e4.2.2.yaml"
exp_names[3]="e4.2.3.yaml"
exp_names[4]="e4.2.4.yaml"
exp_names[5]="e4.3.1.yaml"
exp_names[6]="e4.3.2.yaml"
exp_names[7]="e4.3.3.yaml"
exp_names[8]="e4.3.4.yaml"
exp_names[9]="e4.7.1.yaml"

for exp_idx in "${!exp_names[@]}"; 
do
    CRONTAB_DIR=/home/workspace/experiments
    DATASET_NAME=diaasq
    MODEL_NAME=gpt4omini
    echo "${param_names[$exp_idx]} | ${exp_names[$exp_idx]}"
    
    bash $CRONTAB_DIR/run_experiment.sh $MODEL_NAME "${param_names[$exp_idx]}" "${exp_names[$exp_idx]}" $DATASET_NAME >> qa_log.txt 2>&1
done