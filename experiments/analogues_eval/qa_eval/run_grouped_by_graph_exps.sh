#!/usr/bin/bash

BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI/experiments/analogues_eval/qa_eval

TMP_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_BASE_DIR/deployment"
MLFLOW_DEPLOYMENT_COMPOSE_PATH="$TMP_DEPLOYMENT_COMPOSE_PATH/mlflow"
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
USERNAME=root

CONFIGURE_ENV_DIR="$BASE_DIR/configure"
CREATE_ENVFILE_SCRIPT="$CONFIGURE_ENV_DIR/prepare_env_files.sh"
ENV_SETTINGS_DIR="$CONFIGURE_ENV_DIR/../env_settings"

# ===============================================================

DATASETS=("hotpotqa_distractor_validation") # TO CHANGE
KNOWLEDGE_GRAPHS=("llama318b_230126_v2prompts") # TO CHANGE
EVAL_FNAMES=("hotpotqa_distractor_validation.yaml") # TO CHANGE
CONFIGURE_FNAMES=("hotpotqa_distractor_validation.yaml") # TO CHANGE
METHOD_NAMES=("hipporag") # TO CHANGE

# ===============================================================

TMP_METHOD_QAEVAL_UTILS_DIR="$BASE_DIR/../available_methods_utils/$METHOD/qa_eval"
TMP_METHOD_ENVFILE_YAML="$TMP_METHOD_KGEVAL_UTILS_DIR/qaenv_params.yaml"

# ===============================================================

#cd $MLFLOW_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env" up -d mlflow

for ds_idx in "${!DATASETS[@]}";
do
    CURRENT_METHOD="${METHOD_NAMES[$ds_idx]}"
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    CURRENT_EVAL_FNAME="${EVAL_FNAMES[$ds_idx]}"
    CURRENT_CONFIGURE_FNAME="${CONFIGURE_FNAMES[$ds_idx]}"

    echo "$CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG"

    # -----------------------------------------------------------
    # 1. Создание env-файла для exp-окружения
    SPEC_ENV_SETTINGS_DIR="$ENV_SETTINGS_DIR/$CURRENT_METHOD/$CURRENT_DATASET/$CURRENT_KG"

    echo $SPEC_ENV_SETTINGS_DIR
    echo $TMP_METHOD_ENVFILE_YAML

    # 1.1 Запускаем TMP workspace-контейнер
    cd $TMP_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env_base" up -d workspace
    # 1.2 Редактируем нужные значения в qaenv_params-файле
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".DATASET_NAME = \"$CURRENT_DATASET\"" $TMP_METHOD_ENVFILE_YAML
    docker exec -u $USERNAME $TMP_WORKSPACE_CNTNAME yq -iy ".KNOWLEDGE_GRAPH_NAME = \"$CURRENT_KG\"" $TMP_METHOD_ENVFILE_YAML
    # 1.3 Выключаем TMP workspace-контейнер
    docker stop $TMP_WORKSPACE_CNTNAME ; docker rm $TMP_WORKSPACE_CNTNAME
    # 1.4 Создаём директорию для сохранения env-файла по конкретному графу знаний
    mkdir -p $SPEC_ENV_SETTINGS_DIR
    # 1.5 Генерируем env-файл
    cd $CONFIGURE_ENV_DIR && bash $CREATE_ENVFILE_SCRIPT $TMP_METHOD_ENVFILE_YAML

    # -----------------------------------------------------------
    # 2. Запуск окружения для проведения QA-экспериментов по конкретному графу знаний
    SPEC_ENV_SETTINGS="$SPEC_ENV_SETTINGS_DIR/.qaexp_env"

    echo $SPEC_ENV_SETTINGS

    cd $CONFIGURE_ENV_DIR ; docker compose --env-file="$SPEC_ENV_SETTINGS" up -d workspace

    # -----------------------------------------------------------
    # 3. подготовить QA-конфиги
    EXPENV_BASE_DIR=/home/workspace/experiments/analogues_eval/qa_eval
    PARAMS_TO_RUN_DIR="$EXPENV_BASE_DIR/params_to_run/"
    PREPARED_PARAMS_DIR="$TMP_METHOD_QAEVAL_UTILS_DIR/prepared_params/$CURRENT_DATASET/$CURRENT_KG/"
    WORKSPACE_EXP_CNTNAME="personalai_mmenschikov_analogues_qaexp_workspace_$CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG"

    echo $PARAMS_TO_RUN_DIR
    echo $PREPARED_PARAMS_DIR
    echo $WORKSPACE_EXP_CNTNAME

    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "rm -rf $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "mkdir $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash -c "cp $PREPARED_PARAMS_DIR/* $PARAMS_TO_RUN_DIR"

    # -----------------------------------------------------------
    # 4. Запустить QA-эксперименты
    docker exec -u $USERNAME $WORKSPACE_EXP_CNTNAME bash $EXPENV_BASE_DIR/crontab_job.sh $CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG $CURRENT_CONFIGURE_FNAME $CURRENT_EVAL_FNAME

    # -----------------------------------------------------------
    # 5. Удаление конкретного QA-окружения
    cd $CONFIGURE_ENV_DIR ; bash rm_containers.sh $CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (run_grouped_by_graph_exps.sh) ==="
