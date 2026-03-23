#!/usr/bin/bash
echo "Создание директории (c необходимыми конфигурационными файлами) для конкретного эксперимента"

EXP_BASE_DIR=/home/workspace/experiments/analogues_eval/qa_eval
PYTHON_CMD=/usr/bin/python3

# --------------------------------------------------------

QAHYPERP_PARAMS_PATH=$1
EXPDIR_PARAMS_PATH=$2

# --------------------------------------------------------

BASE_CONFIGURE_DIR="$EXP_BASE_DIR/configure"

# --------------------------------------------------------

INIT_EXP_SCIPT="$BASE_CONFIGURE_DIR/init_file_structure.py"
INIT_LOG_PATH="$BASE_CONFIGURE_DIR/initdir_log.txt"

# --------------------------------------------------------

$PYTHON_CMD $INIT_EXP_SCIPT $QAHYPERP_PARAMS_PATH $EXPDIR_PARAMS_PATH >> $INIT_LOG_PATH 2>&1

echo "=== Done (init_exp_environment.sh) ==="
