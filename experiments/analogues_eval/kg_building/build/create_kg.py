print("Start Knowledge Graph creation ...")
import sys
import json
import datetime
import yaml
from time import time

EXPERIMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPERIMETS_BASE_PATH)
from analogues_eval.available_methods_utils.config import AVAILABLE_GRAPHRAG_BUILD_METHODS, GraphRAGBuildOperations
from analogues_eval.load_dataset.kgbuild_datasets import CUSTOM_LOAD_KGBUILD_DS_FUNCS

from ollama_proxy import OllamaProxyMetrics

OLLAMA_ENDPOINTS = {
    'hipporag2': '/v1/chat/completions',
    'lightrag': '/v1/chat/completions',
    'raptor': '/v1/chat/completions'
}

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

print("5.1. Ollama metrics before run (pay attention: require separate container with ollama-proxy)")
print(f"- endpoint: {OLLAMA_ENDPOINTS[KGHYPERP_PARAMS['METHOD_NAME']]}")

ollama_stats = OllamaProxyMetrics()
ollama_metrics_before_run = {
    'ollama_requests_total': ollama_stats.get(
        "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[KGHYPERP_PARAMS['METHOD_NAME']],"model": method_config['llm_model_name']}),
    'ollama_prompt_tokens_total': ollama_stats.get(
        "ollama_prompt_tokens_total", "counter", {'model': method_config['llm_model_name']}),
    'ollama_completion_tokens_total': ollama_stats.get(
        "ollama_completion_tokens_total", "counter", {'model': method_config['llm_model_name']})
}
for k, v in ollama_metrics_before_run.items():
    print(f"- {k}: {v}")

####################################################

print("6. Run KG build process")
start_time = time()
print(f"start time: {datetime.datetime.now()}")

docs = [doc_info[0] for doc_info in dataset]
method_main.build_graph(docs)

end_time = time()
print(f"end time: {datetime.datetime.now()}")
elapsed_time_seconds = round(end_time - start_time, 3)
print(f"Elapsed time: {round(elapsed_time_seconds / 60, 2)} minutes | {round((elapsed_time_seconds / 60) / 60, 2)} hours")


print("graph info:")
method_main.print_graph_info()

####################################################
print("6.1. Ollama metrics after run (pay attention: require separate container with ollama-proxy)")
print(f"- endpoint: {OLLAMA_ENDPOINTS[KGHYPERP_PARAMS['METHOD_NAME']]}")
ollama_stats = OllamaProxyMetrics()
ollama_metrics_after_run = {
    'ollama_requests_total': ollama_stats.get(
        "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[KGHYPERP_PARAMS['METHOD_NAME']], "model": method_config['llm_model_name']}),
    'ollama_prompt_tokens_total': ollama_stats.get(
        "ollama_prompt_tokens_total", "counter", {'model': method_config['llm_model_name']}),
    'ollama_completion_tokens_total': ollama_stats.get(
        "ollama_completion_tokens_total", "counter", {'model': method_config['llm_model_name']})
}
for k, v in ollama_metrics_after_run.items():
    print(f"- {k}: {v}")

####################################################
print("6.2. Ollama metrics diff")
for k in ollama_metrics_before_run.keys():
    print(f"- {k}: {ollama_metrics_after_run[k]-ollama_metrics_before_run[k]}")

####################################################
print("7. Saving graph")

method_main.save_graph(KGENV_PARAMS, KGHYPERP_PARAMS)

print("############ DONE ############")
