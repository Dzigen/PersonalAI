#!/usr/bin/bash

LOCAL_PERSONALAI_BASE_PATH=/home/m.menschikov/workspace/personal_ai/Personal-AI
LOCAL_KGEVAL_BASE_PATH="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/kg_eval/mine"

TMP_PERSONALAI_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_PERSONALAI_BASE_DIR/deployment"
MLFLOW_DEPLOYMENT_COMPOSE_PATH="$TMP_DEPLOYMENT_COMPOSE_PATH/mlflow"
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
USERNAME=root

# ===============================================================

METHOD="hipporag2" # TO CHANGE
DATASET="mine_train_kgeval" # TO CHANGE
KNOWLEDGE_GRAPHS=("llama318b_110226_v2prompts" "qwen257b_110226_v2prompts" "granite338b_110226_v2prompts" "gemma29b_110226_v2prompts") # TO CHANGE
EVAL_FNAME="eval_params.yaml" # TO CHANGE
CONFIGURE_FNAME="expdir_params.yaml" # TO CHANGE

# ===============================================================

INIT_ENV_DIR="$TMP_PERSONALAI_BASE_DIR/experiments/kg_eval/mine/init_env"
CREATE_ENVFILE_SCRIPT="$INIT_ENV_DIR/prepare_env_files.sh"
CREATE_ENVFILE_YAML="$INIT_ENV_DIR/kgevalenv_params.yaml"
ENV_SETTINGS_DIR="$INIT_ENV_DIR/env_settings"

# ===============================================================

#cd $MLFLOW_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env" up -d mlflow

for kg_idx in "${!KNOWLEDGE_GRAPHS[@]}";
do
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"

    echo "$DATASET $CURRENT_KG"

    # -----------------------------------------------------------
    # 1. Создание env-файла для exp-окружения
    SPEC_ENV_SETTINGS_DIR="$ENV_SETTINGS_DIR/$DATASET/$CURRENT_KG"

    echo $SPEC_ENV_SETTINGS_DIR
    echo $CREATE_ENVFILE_YAML

    # 1.1 Запускаем TMP workspace-контейнер
    cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
    # 1.2 Редактируем нужные значения в qaenv_params-файле
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".DATASET_NAME = \"$DATASET\"" $CREATE_ENVFILE_YAML
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".KNOWLEDGE_GRAPH_NAME = \"$CURRENT_KG\"" $CREATE_ENVFILE_YAML
    # 1.3 Выключаем TMP workspace-контейнер
    docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME
    # 1.4 Создаём директорию для сохранения env-файла по конкретному графу знаний
    mkdir -p $SPEC_ENV_SETTINGS_DIR
    # 1.5 Генерируем env-файл
    cd $INIT_ENV_DIR && bash $CREATE_ENVFILE_SCRIPT $CREATE_ENVFILE_YAML

    # -----------------------------------------------------------
    # 2. Запуск окружения для оценки качества построенного графа
    SPEC_ENV_SETTINGS="$SPEC_ENV_SETTINGS_DIR/.kgeval_env"
    SPEC_EXP_WORKSPACE_CNTNAME="personalai_mmenschikov_kgeval_workspace_$DATASET\_$CURRENT_KG"

    echo $SPEC_ENV_SETTINGS

    cd $INIT_ENV_DIR ; docker compose --env-file="$SPEC_ENV_SETTINGS" up -d workspace

    # -----------------------------------------------------------
    # 3. подготовить KGEVAL-конфиги
    EXPENV_BASE_DIR=/home/workspace/experiments/kg_eval/mine
    PARAMS_TO_RUN_DIR="$EXPENV_BASE_DIR/params_to_run/"
    PREPARED_PARAMS_DIR="$EXPENV_BASE_DIR/configure/prepared_params/$DATASET/$CURRENT_KG/"
    WORKSPACE_EXP_CNTNAME=personalai_mmenschikov_kgeval_workspace_$DATASET\_$CURRENT_KG

    echo $PARAMS_TO_RUN_DIR
    echo $PREPARED_PARAMS_DIR
    echo $WORKSPACE_EXP_CNTNAME

    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "rm -rf $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "mkdir $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "cp $PREPARED_PARAMS_DIR/* $PARAMS_TO_RUN_DIR"

    # -----------------------------------------------------------
    # 4. Запустить QA-эксперименты
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash $EXPENV_BASE_DIR/crontab_job.sh $CURRENT_KG $DATASET $CONFIGURE_FNAME $EVAL_FNAME

    # -----------------------------------------------------------
    # 5. Удаление конкретного QA-окружения
    cd $INIT_ENV_DIR ; bash rm_containers.sh $DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (run_grouped_by_graph_exps.sh) ==="
