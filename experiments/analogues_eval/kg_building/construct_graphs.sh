#!/usr/bin/bash

LOCAL_METHODS_KGBUIKD_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/experiments/analogues_eval/kg_building # TO CHANGE
WORKSPACE_METHODS_KGBUILD_BASE_DIR=/home/workspace/experiments/analogues_eval/kg_building
USERNAME=root

# ===============================================================

DATASETS=("diaasq" "natural_questions_train" "trivia_qa_rcwikipedia_validation" "diaasq" "natural_questions_train" "trivia_qa_rcwikipedia_validation")  # TO CHANGE
KNOWLEDGE_GRAPHS=("gemma29b_260226" "gemma29b_270226" "gemma29b_280226" "gemma312b_070326" "gemma312b_080326" "gemma312b_090326") # TO CHANGE
METHODS=("hipporag2" "hipporag2" "hipporag2" "hipporag2" "hipporag2" "hipporag2") # TO CHANGE

# ===============================================================

for ds_idx in "${!DATASETS[@]}";
do
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    CURRENT_METHOD="${METHODS[$ds_idx]}"
    WORKSPACE_CNTNAME=personalai_mmenschikov_analogues_kgbuild_workspace_$CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG

    echo $CURRENT_METHOD
    echo $CURRENT_DATASET
    echo $CURRENT_KG

    # init graph
    cd $LOCAL_METHODS_KGBUIKD_BASE_DIR ; bash init_graph.sh $CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG
    # build graph
    docker exec -u $USERNAME $WORKSPACE_CNTNAME bash $WORKSPACE_METHODS_KGBUILD_BASE_DIR/crontab_job.sh $CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG

    # rm containers
    cd $LOCAL_METHODS_KGBUIKD_BASE_DIR ; bash rm_containers.sh $CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (construct_graphs.sh) ==="
