print("Start Knowledge Graph creation ...")
import sys
import json
import datetime
import yaml

EXPERIMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPERIMETS_BASE_PATH)
from analogues_eval.available_methods_utils.config import AVAILABLE_GRAPHRAG_BUILD_METHODS, GraphRAGBuildOperations
from analogues_eval.load_dataset.kgbuild_datasets import CUSTOM_LOAD_KGBUILD_DS_FUNCS

####################################################
print("1. Loading hyperparameters from .yaml files")

KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

WORKSPACE_METHOD_KGS_PATH=f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['METHOD_NAME']}"
WORKSPACE_SPEC_KG_PATH = f"{WORKSPACE_METHOD_KGS_PATH}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
METHOD_CONFIG_PATH = f"{WORKSPACE_SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['method_config']}"

DATASET_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}"

####################################################
print("3. Loading configs")

with open(METHOD_CONFIG_PATH, 'r', encoding='utf-8') as fd:
    method_config = json.loads(fd.read())

print("METHOD CONFIG:\n", method_config)

####################################################
print("4. Loading dataset")

dataset = CUSTOM_LOAD_KGBUILD_DS_FUNCS[KGHYPERP_PARAMS['DATASET_NAME']](DATASET_PATH)
print(DATASET_PATH)
print(len(dataset))

####################################################
print("5. Initializing method main class")

method_main: GraphRAGBuildOperations = AVAILABLE_GRAPHRAG_BUILD_METHODS[KGHYPERP_PARAMS['METHOD_NAME']](method_config)

print("graph info:")
method_main.print_graph_info()

####################################################
print("6. Run KG build process")
print(f"start time: {datetime.datetime.now()}")

docs = [doc_info[0] for doc_info in dataset]
method_main.build_graph(docs)

print(f"end time: {datetime.datetime.now()}")

print("graph info:")
method_main.print_graph_info()

####################################################
print("7. Saving graph")

method_main.save_graph(KGENV_PARAMS, KGHYPERP_PARAMS)

print("############ DONE ############")
