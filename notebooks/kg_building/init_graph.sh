#!/usr/bin/bash

TMP_DEPLOYMENT_COMPOSE_PATH=/home/m.menschikov/workspace/personal_ai/Personal-AI/deployment
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/
TMP_KGCREATE_PATH="$TMP_BASE_DIR/notebooks/kg_building/create"
TMP_KGS_PATH="$TMP_BASE_DIR/data/knowledge_graphs"
TMP_PARAMS_PATH="$TMP_KGCREATE_PATH/params.yaml"

DATASET_NAME=$1
KG_NAME=$2
MAIN_WORKSPACE_CNTNAME=$TMP_WORKSPACE_CNTNAME\_$DATASET_NAME\_$KG_NAME
MAIN_KGCREATE_PATH=/home/workspace/notebooks/kg_building/create
MAIN_PARAMS_PATH="$MAIN_KGCREATE_PATH/params.yaml"

PYTHON_CMD=/usr/bin/python3

# поднять tmp workspace-контейнер
cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file="$TMP_DEPLOYMENT_COMPOSE_PATH/.env_base" up -d workspace
# инициализировать структуру графа
docker exec $TMP_WORKSPACE_CNTNAME $PYTHON_CMD "$TMP_KGCREATE_PATH/init_file_structure.py" $TMP_PARAMS_PATH
# создать env-файл
docker exec $TMP_WORKSPACE_CNTNAME $PYTHON_CMD "$TMP_KGCREATE_PATH/get_dc_envfile.py" $TMP_PARAMS_PATH
docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME

# создать окружение графа
cd "$TMP_KGCREATE_PATH/.." ; docker compose --env-file="$TMP_KGS_PATH/$DATASET_NAME/$KG_NAME/.env" up -d workspace
# сохранить конфигурационные файлы mem-пайплайна
docker exec $MAIN_WORKSPACE_CNTNAME pip install pymilvus
docker exec $MAIN_WORKSPACE_CNTNAME systemctl start cron
# сохранить конфигурационные файлы mem-пайплайна
docker exec $MAIN_WORKSPACE_CNTNAME $PYTHON_CMD "$MAIN_KGCREATE_PATH/prepare_gm_configs.py" $MAIN_PARAMS_PATH
