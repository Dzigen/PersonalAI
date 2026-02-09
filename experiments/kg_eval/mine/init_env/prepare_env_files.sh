#!/usr/bin/bash

TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_BASE_DIR/deployment"

TMP_QAEXP_PATH="$TMP_BASE_DIR/experiments/kg_eval/mine"
TMP_INITENV_PATH="$TMP_QAEXP_PATH/init_env"
TMP_QAENV_PARAMS_PATH="$TMP_INITENV_PATH/kgevalenv_params.yaml"

USERNAME=m.menschikov
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
PYTHON_CMD=/usr/bin/python3

# поднять tmp workspace-контейнер
cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
# создать env-файл
docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME $PYTHON_CMD "$TMP_INITENV_PATH/get_dc_envfile.py" $TMP_QAENV_PARAMS_PATH
# удалить tmp-конейнер
docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME
