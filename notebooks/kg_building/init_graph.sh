#!/usr/bin/bash

TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_BASE_DIR/deployment" 
TMP_CREATE_DIR="$TMP_BASE_DIR/notebooks/kg_building"
TMP_KGCREATE_PATH="$TMP_BASE_DIR/notebooks/kg_building/create"

DATASET_NAME=$1
KG_NAME=$2
USERNAME=m.menschikov

ENV_FILE_PATH="/mnt/data/m.menschikov/personalai/knowledge_graphs/$DATASET_NAME/$KG_NAME/.env"

TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
MAIN_WORKSPACE_CNTNAME=personalai_mmenschikov_kgbuild_workspace\_$DATASET_NAME\_$KG_NAME

BASE_CONTAINER_PATH=/home/workspace
MAIN_KGCREATE_PATH="$BASE_CONTAINER_PATH/notebooks/kg_building/create"
CONTAINER_WORKSPACE_KG_PATH="$BASE_CONTAINER_PATH/data/knowledge_graphs/$DATASET_NAME/$KG_NAME"

TMP_KGCONN_PARAMS_PATH="$TMP_KGCREATE_PATH/kgconn_params.yaml"
TMP_KGENV_PARAMS_PATH="$TMP_KGCREATE_PATH/kgenv_params.yaml"
TMP_KGHYPERP_PARAMS_PATH="$TMP_KGCREATE_PATH/kghyperp_params.yaml"

KGCONN_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kgconn_params.yaml"
KGENV_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kgenv_params.yaml"
KGHYPERP_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kghyperp_params.yaml"

PYTHON_CMD=/usr/bin/python3

# поднять tmp workspace-контейнер
cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
# инициализировать структуру графа
docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME $PYTHON_CMD "$TMP_KGCREATE_PATH/init_file_structure.py" $TMP_KGENV_PARAMS_PATH $TMP_KGHYPERP_PARAMS_PATH
# создать env-файл
docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME $PYTHON_CMD "$TMP_KGCREATE_PATH/get_dc_envfile.py" $TMP_KGCONN_PARAMS_PATH $TMP_KGENV_PARAMS_PATH $TMP_KGHYPERP_PARAMS_PATH

SPARSE_DIR_PATH="$TMP_BASE_DIR/data/knowledge_graphs/$DATASET_NAME/$KG_NAME/embeddings_part/sparse_vectors_volume"
docker exec -u root $TMP_WORKSPACE_CNTNAME sh -c "chown -R 1000:1000 $SPARSE_DIR_PATH"

# удалить tmp-конейнер
docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME

# создать окружение графа
cd $TMP_CREATE_DIR ; docker compose --env-file=$ENV_FILE_PATH up -d workspace
docker exec -u root $MAIN_WORKSPACE_CNTNAME systemctl start cron

# создать конфигурационный файл kg-модели
docker exec -u root $MAIN_WORKSPACE_CNTNAME $PYTHON_CMD "$MAIN_KGCREATE_PATH/prepare_kg_config.py" $KGCONN_PARAMS_PATH $KGENV_PARAMS_PATH $KGHYPERP_PARAMS_PATH
# создать конфигурационный файл mem-пайплайна
docker exec -u root  $MAIN_WORKSPACE_CNTNAME $PYTHON_CMD  "$MAIN_KGCREATE_PATH/prepare_mem_config.py" $KGENV_PARAMS_PATH $KGHYPERP_PARAMS_PATH
# создать конфигурационные файлы кешей
docker exec -u root $MAIN_WORKSPACE_CNTNAME $PYTHON_CMD  "$MAIN_KGCREATE_PATH/prepare_cache_configs.py" $KGCONN_PARAMS_PATH $KGENV_PARAMS_PATH $KGHYPERP_PARAMS_PATH
