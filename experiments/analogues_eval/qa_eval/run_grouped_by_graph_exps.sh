#!/usr/bin/bash

LOCAL_PERSONALAI_BASE_PATH=/home/m.menschikov/workspace/personal_ai/Personal-AI # TO CHANGE
LOCAL_QAEVAL_BASE_PATH="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/qa_eval"


TMP_PERSONALAI_BASE_DIR=/home/m.menschikov/workspace/personal_ai/Personal-AI
TMP_DEPLOYMENT_COMPOSE_PATH="$TMP_PERSONALAI_BASE_DIR/deployment"
MLFLOW_DEPLOYMENT_COMPOSE_PATH="$TMP_DEPLOYMENT_COMPOSE_PATH/mlflow"
TMP_WORKSPACE_CNTNAME=personalai_mmenschikov_workspace
USERNAME=root

# ===============================================================

DATASETS=("diaasq" "natural_questions_train" "trivia_qa_rcwikipedia_validation" "diaasq" "natural_questions_train" "trivia_qa_rcwikipedia_validation") # TO CHANGE
KNOWLEDGE_GRAPHS=("gemma29b_260226" "gemma29b_270226" "gemma29b_280226" "gemma312b_070326" "gemma312b_080326" "gemma312b_090326") # TO CHANGE
EVAL_FNAMES=("diaasq.yaml" "natural_questions_train.yaml" "trivia_qa_rcwikipedia_validation.yaml" "diaasq.yaml" "natural_questions_train.yaml" "trivia_qa_rcwikipedia_validation.yaml") # TO CHANGE
CONFIGURE_FNAMES=("diaasq.yaml" "natural_questions_train.yaml" "trivia_qa_rcwikipedia_validation.yaml" "diaasq.yaml" "natural_questions_train.yaml" "trivia_qa_rcwikipedia_validation.yaml") # TO CHANGE
METHOD_NAMES=("hipporag2" "hipporag2" "hipporag2" "hipporag2" "hipporag2" "hipporag2") # TO CHANGE

# ===============================================================

TMP_ENVCONFIGURE_DIR="$TMP_PERSONALAI_BASE_DIR/experiments/analogues_eval/qa_eval/configure"
TMP_CREATE_ENVFILE_SCRIPT="$TMP_ENVCONFIGURE_DIR/prepare_env_files.sh"

LOCAL_ENV_SETTINGS_DIR="$TMP_PERSONALAI_BASE_DIR/experiments/analogues_eval/qa_eval/env_settings"

WORKSPACE_PERSONALAI_BASE_PATH=/home/workspace
WORKSPACE_QAEVAL_BASE_DIR="$WORKSPACE_PERSONALAI_BASE_PATH/experiments/analogues_eval/qa_eval"

# ===============================================================

#cd $MLFLOW_DEPLOYMENT_COMPOSE_PATH ; docker compose --env-file=".env" up -d mlflow

for ds_idx in "${!DATASETS[@]}";
do
    CURRENT_METHOD="${METHOD_NAMES[$ds_idx]}"
    CURRENT_DATASET="${DATASETS[$ds_idx]}"
    CURRENT_KG="${KNOWLEDGE_GRAPHS[$ds_idx]}"
    CURRENT_EVAL_FNAME="${EVAL_FNAMES[$ds_idx]}"
    CURRENT_CONFIGURE_FNAME="${CONFIGURE_FNAMES[$ds_idx]}"

    TMP_METHOD_QAEVAL_UTILS_DIR="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$CURRENT_METHOD/qa_eval"
    TMP_METHOD_ENVFILE_YAML="$TMP_METHOD_QAEVAL_UTILS_DIR/qaenv_params.yaml"
    LOCAL_INIT_ENV_DIR="$LOCAL_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$CURRENT_METHOD/init_env"
    WORKSPACE_METHOD_QAEVAL_UTILS_DIR="$WORKSPACE_PERSONALAI_BASE_PATH/experiments/analogues_eval/available_methods_utils/$CURRENT_METHOD/qa_eval"
    echo "$CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG"

    SPEC_WORKSPACE_CNTNAME=personalai_mmenschikov_analogues_qaexp_workspace_$CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG

    # -----------------------------------------------------------
    # 1. Создание env-файла для exp-окружения
    SPEC_ENV_SETTINGS_DIR="$LOCAL_ENV_SETTINGS_DIR/$CURRENT_METHOD/$CURRENT_DATASET/$CURRENT_KG"

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
    cd $TMP_ENVCONFIGURE_DIR && bash $TMP_CREATE_ENVFILE_SCRIPT $TMP_METHOD_ENVFILE_YAML

    # -----------------------------------------------------------
    # 2. Запуск окружения для проведения QA-экспериментов по конкретному графу знаний
    SPEC_ENV_SETTINGS="$SPEC_ENV_SETTINGS_DIR/.qaexp_env"

    echo $SPEC_ENV_SETTINGS

    cd $LOCAL_INIT_ENV_DIR ; docker compose --env-file="$SPEC_ENV_SETTINGS" up -d workspace

    # -----------------------------------------------------------
    # 3. подготовить QA-конфиги
    PARAMS_TO_RUN_DIR="$WORKSPACE_QAEVAL_BASE_DIR/params_to_run/"
    PREPARED_PARAMS_DIR="$WORKSPACE_METHOD_QAEVAL_UTILS_DIR/prepared_params/$CURRENT_DATASET/$CURRENT_KG"

    echo $PARAMS_TO_RUN_DIR
    echo $PREPARED_PARAMS_DIR
    echo $SPEC_WORKSPACE_CNTNAME

    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "rm -rf $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "mkdir $PARAMS_TO_RUN_DIR"
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash -c "cp $PREPARED_PARAMS_DIR/* $PARAMS_TO_RUN_DIR"

    # lingua-language-detector

    # -----------------------------------------------------------
    # 4. Запустить QA-эксперименты
    docker exec -u $USERNAME $SPEC_WORKSPACE_CNTNAME bash $WORKSPACE_QAEVAL_BASE_DIR/crontab_job.sh $CURRENT_METHOD $CURRENT_DATASET $CURRENT_KG $CURRENT_CONFIGURE_FNAME $CURRENT_EVAL_FNAME

    # -----------------------------------------------------------
    # 5. Удаление конкретного QA-окружения
    cd $TMP_ENVCONFIGURE_DIR ; bash rm_containers.sh $CURRENT_METHOD\_$CURRENT_DATASET\_$CURRENT_KG
done

# ===============================================================

echo "=== Done (run_grouped_by_graph_exps.sh) ==="
