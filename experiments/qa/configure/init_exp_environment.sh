#!/usr/bin/bash
# Создание директории (c необходимыми конфигурационными файлами) для конкретного эксперимента

EXP_BASE_DIR=/home/workspace/experiments/qa
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

QAHYPERP_PARAMS_PATH=$1
EXPDIR_PARAMS_PATH=$2

# --------------------------------------------------------

BASE_CONFIGURE_DIR="$EXP_BASE_DIR/configure"

# --------------------------------------------------------

INIT_EXP_SCIPT="$BASE_CONFIGURE_DIR/init_file_structure.py"
PRE_QACONFIG_SCRIPT="$BASE_CONFIGURE_DIR/prepare_qa_configs.py"

INIT_LOG_PATH="$BASE_CONFIGURE_DIR/initdir_log.txt"
GENCONFIGS_LOG_PATH="$BASE_CONFIGURE_DIR/genconfigs_log.txt"

# --------------------------------------------------------

$PYTHON_CMD $INIT_EXP_SCIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $INIT_LOG_PATH 2>&1

$PYTHON_CMD $PRE_QACONFIG_SCRIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $GENCONFIGS_LOG_PATH 2>&1

echo "=== Done (init_exp_environment.sh) ==="
