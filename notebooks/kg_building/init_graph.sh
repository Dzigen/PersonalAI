#!/usr/bin/bash

TMP_DEPLOYMENT_COMPOSE_PATH=$1
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_worksapce

PARAMS_PATH=$2

DATASET_NAME=$3
KG_NAME=$4
MAIN_WORKSPACE_CNTNAME=$TMP_WORKSPACE_CNTNAME\_$DATASET_NAME\_$KG_NAME

KGBUILDING_BASE_PATH=/home/workspace/notebooks/kg_building
KGS_BASE_PATH=/home/workspace/data/knowledge_graphs
PYTHON_CMD=/usr/bin/python3


# поднять tmp workspace-контейнер
cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file="$TMP_DEPLOYMENT_COMPOSE_PATH/.env_base" up -d workspace
# создать env-файл
docker exec $TMP_WORKSPACE_CNTNAME bash -c 'cd "$KGBUILDING_BASE_PATH/create" ; $PYTHON_CMD get_dc_envfile.py $PARAMS_PATH'
docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME

# создать окружение графа
cd $KGBUILDING_BASE_PATH ; docker compose --env-file="$KGS_BASE_PATH/$CUR_KG_REL_PATH/.env" up -d workspace

# инициализировать структуру графа
docker exec $MAIN_WORKSPACE_CNTNAME bash -c 'cd "$KGBUILDING_BASE_PATH/create" ; $PYTHON_CMD init_file_structure.py $PARAMS_PATH'
# сохранить конфигурационные файлы mem-пайплайна
docker exec $MAIN_WORKSPACE_CNTNAME bash -c 'cd "$KGBUILDING_BASE_PATH/create" ; $PYTHON_CMD prepare_gm_configs.py $PARAMS_PATH'
