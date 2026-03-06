#!/usr/bin/bash

BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/notebooks/kg_building
WORKSPACE_BASE_DIR=/home/workspace/notebooks/kg_building
USERNAME=root

# ===============================================================

DATASETS=("hotpotqa_distractor_validation" "trivia_qa_rcwikipedia_validation" "diaasq" "natural_questions_train" "musique_validation" "2wikimultihopqa_dev")  # TO CHANGE
KNOWLEDGE_GRAPHS=("gemma312b_010326_v2prompts" "gemma312b_020326_v2prompts" "gemma312b_030326_v2prompts" "gemma312b_040326_v2prompts" "gemma312b_050326_v2prompts" "gemma312b_060326_v2prompts") # TO CHANGE

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