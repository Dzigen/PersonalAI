#!/usr/bin/bash

DATASET_NAME=$1
KG_NAME=$2

TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_BASE_DIR/deployment" 

cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d empty_workspace

CONTAINER_KG_PATH="/mnt/data/m.menschikov/personalai/knowledge_graphs/$DATASET_NAME/$KG_NAME"
echo $CONTAINER_KG_PATH
docker exec personalai_mmenschikov_emptyworkspace sh -c "rm -rf $CONTAINER_KG_PATH"
docker stop personalai_mmenschikov_emptyworkspace; docker rm personalai_mmenschikov_emptyworkspace