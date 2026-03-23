#!/usr/bin/bash

METHOD=$1
DATASET_NAME=$2
KG_NAME=$3

LOCAL_KGS_PATH=/mnt/data/m.menschikov/personalai/knowledge_graphs/analogues_eval # TO CHANGE
LOCAL_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI # TO CHANGE
LOCAL_DEPLOYMENT_COMPOSE_PATH="$LOCAL_BASE_DIR/deployment"

cd $LOCAL_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d empty_workspace

CONTAINER_KG_PATH="$LOCAL_KGS_PATH/$METHOD/$DATASET_NAME/$KG_NAME"
echo $CONTAINER_KG_PATH
docker exec personalai_mmenschikov_emptyworkspace sh -c "rm -rf $CONTAINER_KG_PATH"
docker stop personalai_mmenschikov_emptyworkspace; docker rm personalai_mmenschikov_emptyworkspace
