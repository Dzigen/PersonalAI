#!/usr/bin/bash

LOCAL_PERSONALAI_BASE_PATH=/home/m.menschikov/workspace/personal_ai/Personal-AI # TO CHANGE
LOCAL_KGEVAL_BASE_PATH="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/kg_eval/mine"

TMP_PERSONALAI_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI # TO CHANGE
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_PERSONALAI_BASE_DIR/deployment"
MLFLOW_DEPLOYMENT_COMPOSE_PATH="$TMP_DEPLOYMENT_COMPOSE_PATH/mlflow"
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
USERNAME=root

# ===============================================================

METHOD="wikontic" # TO CHANGE
DATASET="mine_train_kgeval" # TO CHANGE
KNOWLEDGE_GRAPHS=("qwen2514b_190226_mine_wikontic") # TO CHANGE "qwen2514b_190226_mine_wikontic"
EVAL_FNAME="eval_params.yaml" # TO CHANGE
CONFIGURE_FNAME="expdir_params.yaml" # TO CHANGE

# ===============================================================

TMP_METHOD_KGEVAL_UTILS_DIR="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$METHOD/kg_eval"
TMP_METHOD_ENVFILE_YAML="$TMP_METHOD_KGEVAL_UTILS_DIR/kgevalenv_params.yaml"

TMP_ENVCONFIGURE_DIR="$TMP_PERSONALAI_BASE_DIR/experiments/analogues_eval/kg_eval/mine/configure"
TMP_CREATE_ENVFILE_SCRIPT="$TMP_ENVCONFIGURE_DIR/prepare_env_files.sh"

LOCAL_ENV_SETTINGS_DIR="$LOCAL_KGEVAL_BASE_PATH/env_settings"
LOCAL_INIT_ENV_DIR="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$METHOD/init_env"

WORKSPACE_PERSONALAI_BASE_PATH=/home/workspace
WORKSPACE_KGEVAL_BASE_DIR="$WORKSPACE_PERSONALAI_BASE_PATH/experiments/analogues_eval/kg_eval/mine"
WORKSPACE_METHOD_KGEVAL_UTILS_DIR="$WORKSPACE_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$METHOD/kg_eval"

# ===============================================================

#cd $MLFLOW_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env" up -d mlflow

for kg_idx in "${!KNOWLEDGE_GRAPHS[@]}";
do
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$kg_idx]}"

    echo "$METHOD $DATASET $CURRENT_KG"
    SPEC_WORKSPACE_CNTNAME=personalai_mmenschikov_analogues_kgeval_workspace_$METHOD\_$DATASET\_$CURRENT_KG

    # -----------------------------------------------------------
    # 1. Создание env-файла для exp-окружения
    SPEC_ENV_SETTINGS_DIR="$LOCAL_ENV_SETTINGS_DIR/$METHOD/$DATASET/$CURRENT_KG"

    echo $SPEC_ENV_SETTINGS_DIR
    echo $TMP_METHOD_ENVFILE_YAML

    # 1.1 Запускаем TMP workspace-контейнер
    cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
    # 1.2 Редактируем нужные значения в qaenv_params-файле
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".DATASET_NAME = \"$DATASET\"" $TMP_METHOD_ENVFILE_YAML
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".KNOWLEDGE_GRAPH_NAME = \"$CURRENT_KG\"" $TMP_METHOD_ENVFILE_YAML
    # 1.3 Выключаем TMP workspace-контейнер
    docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME
    # 1.4 Создаём директорию для сохранения env-файла по конкретному графу знаний
    mkdir -p $SPEC_ENV_SETTINGS_DIR
    # 1.5 Генерируем env-файл
    cd $TMP_ENVCONFIGURE_DIR && bash $TMP_CREATE_ENVFILE_SCRIPT $TMP_METHOD_ENVFILE_YAML

    # -----------------------------------------------------------
    # 2. Запуск окружения для оценки качества построенного графа
    SPEC_ENV_SETTINGS="$SPEC_ENV_SETTINGS_DIR/.kgeval_env"

    echo $SPEC_ENV_SETTINGS

    cd $LOCAL_INIT_ENV_DIR ; docker compose --env-file="$SPEC_ENV_SETTINGS" up -d workspace

    # -----------------------------------------------------------
    # 3. подготовить KGEVAL-конфиги
    PARAMS_TO_RUN_DIR="$WORKSPACE_KGEVAL_BASE_DIR/params_to_run/"
    PREPARED_PARAMS_DIR="$WORKSPACE_METHOD_KGEVAL_UTILS_DIR/prepared_params/$DATASET/$CURRENT_KG"

    echo $PARAMS_TO_RUN_DIR
    echo $PREPARED_PARAMS_DIR
    echo $SPEC_WORKSPACE_CNTNAME

    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "rm -rf $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "mkdir $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "cp $PREPARED_PARAMS_DIR/* $PARAMS_TO_RUN_DIR"

    # -----------------------------------------------------------
    # 4. Запустить оценку построенных графов
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash $WORKSPACE_KGEVAL_BASE_DIR/crontab_job.sh $METHOD $DATASET $CURRENT_KG $CONFIGURE_FNAME $EVAL_FNAME

    # -----------------------------------------------------------
    # 5. Удаление конкретного QA-окружения
    cd $TMP_ENVCONFIGURE_DIR ; bash rm_containers.sh $METHOD\_$DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (run_grouped_by_graph_exps.sh) ==="
