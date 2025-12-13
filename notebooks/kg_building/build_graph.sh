#!/usr/bin/bash

NOTEBOOKS_BASE_PATH=/home/workspace/notebooks/kg_building
KG_BASE_PATH=/home/workspace/data/knowledge_graphs

# -----------------------------------------------------------

PYTHON_CMD=/usr/bin/python3
SPEC_KG_RELNAME=$1

# -----------------------------------------------------------

CONTAINER_WORKSPACE_KG_PATH="$KG_BASE_PATH/$SPEC_KG_RELNAME"
KGCONN_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kgconn_params.yaml"
KGENV_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kgenv_params.yaml"
KGHYPERP_PARAMS_PATH="$CONTAINER_WORKSPACE_KG_PATH/settings/kghyperp_params.yaml"

#echo $CONTAINER_WORKSPACE_KG_PATH
#echo $KGCONN_PARAMS_PATH
#echo $KGENV_PARAMS_PATH
#echo $KGHYPERP_PARAMS_PATH

CREATE_SCRIPT="$NOTEBOOKS_BASE_PATH/create/create_kg.py"
HEALTH_SCRIPT="$NOTEBOOKS_BASE_PATH/health_check/check_kg.py"

#echo $CREATE_SCRIPT
#echo $HEALTH_SCRIPT

# -----------------------------------------------------------

cd $CONTAINER_WORKSPACE_KG_PATH ; $PYTHON_CMD $CREATE_SCRIPT $KGCONN_PARAMS_PATH $KGENV_PARAMS_PATH $KGHYPERP_PARAMS_PATH >> create_log.txt 2>&1
cd $CONTAINER_WORKSPACE_KG_PATH ; $PYTHON_CMD $HEALTH_SCRIPT $KGCONN_PARAMS_PATH $KGENV_PARAMS_PATH $KGHYPERP_PARAMS_PATH >> health_log.txt 2>&1
