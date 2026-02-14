#!/usr/bin/bash

WORKSPACE_METHODS_KGBUIKD_BASE_DIR=/home/workspace/experiments/analogues_eval/kg_building
USERNAME=root

# ===============================================================

DATASETS=("hotpotqa_distractor_validation" "hotpotqa_distractor_validation" "hotpotqa_distractor_validation" "hotpotqa_distractor_validation")  # TO CHANGE
KNOWLEDGE_GRAPHS=("llama318b_120226" "qwen257b_120226" "granite338b_120226" "gemma29b_120226") # TO CHANGE
METHODS=("hipporag2" "hipporag2" "hipporag2" "hipporag2") # TO CHANGE

# ===============================================================

for ds_idx in "${!DATASETS[@]}";
do
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    CURRENT_METHOD="${METHODS[$ds_idx]}"

    echo $CURRENT_DATASET
    echo $CURRENT_KG
    echo $CURRENT_METHOD

    # init graph
    cd $WORKSPACE_METHODS_KGBUIKD_BASE_DIR ; bash init_graph.sh $CURRENT_DATASET $CURRENT_KG $CURRENT_METHOD
    # build graph
    cd $WORKSPACE_METHODS_KGBUIKD_BASE_DIR ; bash crontab_job.sh $CURRENT_DATASET $CURRENT_KG $CURRENT_METHOD
done

# ===============================================================

echo "=== Done (construct_graphs.sh) ==="
