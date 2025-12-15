#!/usr/bin/bash

BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/experiments/qa

TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_BASE_DIR/deployment"
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
USERNAME=root

INIT_ENV_DIR="$TMP_BASE_DIR/experiments/qa/init_env"
CREATE_ENVFILE_SCRIPT="$INIT_ENV_DIR/prepare_env_files.sh"
CREATE_ENVFILE_YAML="$INIT_ENV_DIR/qaenv_params.yaml"
ENV_SETTINGS_DIR="$INIT_ENV_DIR/env_settings"

# ===============================================================

DATASETS=("sberdialogues_conv-11" "sberdialogues_conv-12" "sberdialogues_conv-13" "sberdialogues_conv-14" "sberdialogues_conv-15" "sberdialogues_conv-16" "sberdialogues_conv-17" "sberdialogues_conv-18" "sberdialogues_conv-19" "sberdialogues_conv-20") # TO CHANGE
KNOWLEDGE_GRAPHS=("gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts" "gigachatmax_111225_v2prompts") # TO CHANGE
EVAL_FNAMES=("sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml") # TO CHANGE
CONFIGURE_FNAMES=("sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml" "sberdialogues.yaml") # TO CHANGE

# ===============================================================

for ds_idx in "${!DATASETS[@]}";
do  
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    CURRENT_EVAL_FNAME="${EVAL_FNAMES[$ds_idx]}"
    CURRENT_CONFIGURE_FNAME="${CONFIGURE_FNAMES[$ds_idx]}"

    echo "$CURRENT_DATASET $CURRENT_KG"

    # -----------------------------------------------------------
    # 1. Создание env-файла для exp-окружения
    SPEC_ENV_SETTINGS_DIR="$ENV_SETTINGS_DIR/$CURRENT_DATASET/$CURRENT_KG" 

    echo $SPEC_ENV_SETTINGS_DIR
    echo $CREATE_ENVFILE_YAML

    # 1.1 Запускаем TMP workspace-контейнер
    cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
    # 1.2 Устанавливаем нужную утилиту для редактирования yaml-файлов 
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME bash -c "apt install -y jq; pip install yq"
    # 1.3 Редактируем нужные значения в qaenv_params-файле
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".DATASET_NAME = \"$CURRENT_DATASET\"" $CREATE_ENVFILE_YAML
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".KNOWLEDGE_GRAPH_NAME = \"$CURRENT_KG\"" $CREATE_ENVFILE_YAML
    # 1.4 Выключаем TMP workspace-контейнер
    docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME
    # 1.5 Создаём директорию для сохранения env-файла по конкретному графу знаний
    mkdir -p $SPEC_ENV_SETTINGS_DIR
    # 1.6 Генерируем env-файл
    cd $INIT_ENV_DIR && bash $CREATE_ENVFILE_SCRIPT $CREATE_ENVFILE_YAML

    # -----------------------------------------------------------
    # 2. Запуск окружения для проведения QA-экспериментов по конкретному графу знаний
    SPEC_ENV_SETTINGS="$SPEC_ENV_SETTINGS_DIR/.qaexp_env"
    SPEC_EXP_WORKSPACE_CNTNAME="personalai_mmenschikov_qaexp_workspace_$CURRENT_DATASET\_$CURRENT_KG"

    echo $SPEC_ENV_SETTINGS

    cd $INIT_ENV_DIR ; docker compose --env-file="$SPEC_ENV_SETTINGS" up -d workspace

    # -----------------------------------------------------------
    # 3. подготовить QA-конфиги
    EXPENV_BASE_DIR=/home/workspace/experiments/qa
    PARAMS_TO_RUN_DIR="$EXPENV_BASE_DIR/params_to_run/"
    PREPARED_PARAMS_DIR="$EXPENV_BASE_DIR/configure/medium/prepared_params/$CURRENT_DATASET/$CURRENT_KG/"
    WORKSPACE_EXP_CNTNAME=personalai_mmenschikov_qaexp_workspace_$CURRENT_DATASET\_$CURRENT_KG

    echo $PARAMS_TO_RUN_DIR
    echo $PREPARED_PARAMS_DIR
    echo $WORKSPACE_EXP_CNTNAME

    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "rm -rf $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "mkdir $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "cp $PREPARED_PARAMS_DIR/* $PARAMS_TO_RUN_DIR"

    # -----------------------------------------------------------
    # 4. Запустить QA-эксперименты
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash $EXPENV_BASE_DIR/crontab_job.sh $CURRENT_KG $CURRENT_DATASET $CURRENT_CONFIGURE_FNAME $CURRENT_EVAL_FNAME

    # -----------------------------------------------------------
    # 5. Удаление конкретного QA-окружения
    cd $INIT_ENV_DIR ; bash rm_containers.sh $CURRENT_DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (run_grouped_by_graph_exps.sh) ==="