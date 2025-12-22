#!/usr/bin/bash

BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/notebooks/kg_building
WORKSPACE_BASE_DIR=/home/workspace/notebooks/kg_building
USERNAME=root

# ===============================================================

# 15 | 16 (health) | 
DATASETS=("sberdialogues_conv-21" "sberdialogues_conv-22" "sberdialogues_conv-23" "sberdialogues_conv-24" "sberdialogues_conv-25" "sberdialogues_conv-26" "sberdialogues_conv-27" "sberdialogues_conv-28" "sberdialogues_conv-29" "sberdialogues_conv-30" "sberdialogues_conv-31" "sberdialogues_conv-32" "sberdialogues_conv-33" "sberdialogues_conv-34" "sberdialogues_conv-35") # TO CHANGE
KNOWLEDGE_GRAPHS=("gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts") # TO CHANGE

# ===============================================================

for ds_idx in "${!DATASETS[@]}";
do  
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    WORKSPACE_CNTNAME=personalai_mmenschikov_kgbuild_workspace_$CURRENT_DATASET\_$CURRENT_KG

    echo $CURRENT_DATASET
    echo $CURRENT_KG
    echo $WORKSPACE_CNTNAME

    # init graph
    cd $BASE_DIR ; bash init_graph.sh $CURRENT_DATASET $CURRENT_KG
    
    echo "Sleeping for 15 seconds..."
    sleep 15

    # build graph
    docker exec -u $USERNAME $WORKSPACE_CNTNAME bash $WORKSPACE_BASE_DIR/crontab_job.sh $CURRENT_KG $CURRENT_DATASET

    # rm containers
    cd $BASE_DIR ; bash rm_containers.sh $CURRENT_DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (construct_graphs.sh) ==="