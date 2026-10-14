print("Start QA-pipeline inferencing...")
import sys
import yaml
import joblib
from typing import List, Tuple, Dict, Union
from pprint import pprint
import os
import numpy as np
import pandas as pd
from time import time
from tqdm import tqdm
import json

import sys
BASE_PATH = '/home/workspace/experiments/analogues_eval' # TO CHANGE
sys.path.insert(0, BASE_PATH)

from available_methods_utils.config import AVAILABLE_GRAPHRAG_QA_METHOD, GraphRAGQAOperations
from load_dataset.qaeval_datasets import CUSTOM_LOAD_QAEVAL_FUNCS

BASE_PATH2 = '/home/workspace/experiments' # TO CHANGE
sys.path.insert(0, BASE_PATH2)

from ollama_proxy import OllamaProxyMetrics

OLLAMA_ENDPOINTS = {
    'hipporag2': '/v1/chat/completions',
    'lightrag': '/v1/chat/completions',
    'raptor': '/v1/chat/completions'
}

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

CONTAINER_ENV_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg_env_path']}"
SPEC_ENV_PATH = f"{CONTAINER_ENV_PATH}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (qaenv-file)
QAENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['QAENV']}"
with open(QAENV_FILE_PATH, 'r') as stream:
    QAENV_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

# EXP PATHS
EXPS_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXP_RESULTS_DIR = f"{EXPS_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

CONFIGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['configs_name']}"
QA_CONFIG_PATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qa_config']}"

QA_DATASET_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{SPECEXP_PARAMS['DATASET_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_gen_answers_name']}"
GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

QA_ELAPSED_TIME_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"

QA_LLMCALLS_AND_TOKENS_SPATH = f"{SPEC_EXPERIMENT_DIR}/llmcall_and_tokens.json"

# KG PATHS
DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['method_config']}"

QA_CONFIG_SAVE_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qa_config']}"

####################################################
print("3. Loading configs")

with open(KG_MODEL_CONFIG_PATH, 'r', encoding='utf-8') as fd:
    method_config = json.loads(fd.read())

print("KG MODEL_CONFIG:")
pprint(method_config)

qa_config = AVAILABLE_GRAPHRAG_QA_METHOD[SPECEXP_PARAMS['METHOD_NAME']].prepare_qa_config()
print("QA_CONFIG:")
pprint(qa_config)

with open(QA_CONFIG_SAVE_PATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(qa_config, indent=1, ensure_ascii=False))

####################################################
print("4. Loading QA-dataset")

question_packs = CUSTOM_LOAD_QAEVAL_FUNCS[SPECEXP_PARAMS['DATASET_NAME']](QA_DATASET_PATH, SPECEXP_PARAMS['max_samples_per_pack'])
print(QA_DATASET_PATH)
print(len(question_packs), len(question_packs[0][1]))

####################################################
print("5. Initializing method")

method_main: GraphRAGQAOperations = AVAILABLE_GRAPHRAG_QA_METHOD[SPECEXP_PARAMS['METHOD_NAME']](method_config, qa_config)
#method_main.print_graph_info()

####################################################

print("5.1. Ollama metrics before run (pay attention: require separate container with ollama-proxy)")
print(f"- endpoint: {OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']]}")

ollama_stats = OllamaProxyMetrics()
ollama_metrics_before_run = {
    'ollama_requests_total': ollama_stats.get(
        "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']],"model": method_config['llm_model_name']}),
    'ollama_prompt_tokens_total': ollama_stats.get(
        "ollama_prompt_tokens_total", "counter", {'model': method_config['llm_model_name']}),
    'ollama_completion_tokens_total': ollama_stats.get(
        "ollama_completion_tokens_total", "counter", {'model': method_config['llm_model_name']})
}
for k, v in ollama_metrics_before_run.items():
    print(f"- {k}: {v}")

####################################################
print("6. Start inferencing")

for pack_name, questions, _ in question_packs:

    pack_tmp_answers_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_answers_dir):
        os.mkdir(pack_tmp_answers_dir)

    process = tqdm(range(len(questions)))
    for i in process:
        process.set_postfix_str(pack_name)

        ollama_stats = OllamaProxyMetrics()
        ollama_qstart_metrics = {
            'ollama_requests': ollama_stats.get(
                "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']], "model": method_config['llm_model_name']}),
            'ollama_prompt_tokens': ollama_stats.get(
                "ollama_prompt_tokens_total", "counter", {'model': method_config['llm_model_name']}),
            'ollama_completion_tokens': ollama_stats.get(
                "ollama_completion_tokens_total", "counter", {'model': method_config['llm_model_name']})
        }

        s_time = time()
        answer = method_main.perform_qa([questions[i]])[0]
        e_time = time()

        ollama_stats = OllamaProxyMetrics()
        ollama_qend_metrics = {
            'ollama_requests': ollama_stats.get(
                "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']], "model": method_config['llm_model_name']}),
            'ollama_prompt_tokens': ollama_stats.get(
                "ollama_prompt_tokens_total", "counter", {'model': method_config['llm_model_name']}),
            'ollama_completion_tokens': ollama_stats.get(
                "ollama_completion_tokens_total", "counter", {'model': method_config['llm_model_name']})
        }       

        #print("Question: ", questions[i])
        #print("Answer: ", answer)

        answer_dump_file = f"{pack_tmp_answers_dir}/answer_{i}"
        joblib.dump({
            'answer': answer, 
            'elapsed_time': e_time - s_time, 
            'ollama_requests': ollama_qend_metrics['ollama_requests']-ollama_qstart_metrics['ollama_requests'],
            'ollama_prompt_tokens': ollama_qend_metrics['ollama_prompt_tokens']-ollama_qstart_metrics['ollama_prompt_tokens'],
            'ollama_completion_toknes': ollama_qend_metrics['ollama_completion_toknes']-ollama_qstart_metrics['ollama_completion_toknes']
        }, answer_dump_file)

####################################################
print("6.1. Ollama metrics after run (pay attention: require separate container with ollama-proxy)")
print(f"- endpoint: {OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']]}")
ollama_stats = OllamaProxyMetrics()
ollama_metrics_after_run = {
    'ollama_requests_total': ollama_stats.get(
        "ollama_requests_total", "counter", {"endpoint": OLLAMA_ENDPOINTS[SPECEXP_PARAMS['METHOD_NAME']], "model": method_config['llm_model_name']}),
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
print("7. Accumulating generated answers")

def calculate_statistics(values: List[float, int]) -> Dict[str, Union[float, int]]:
    return {
        'count': len(values),
        'max': min(values),
        'mean': round(float(np.mean(values)), 3),
        'median': round(float(np.median(values)), 3),
        'min': min(values),
        'std': round(float(np.std(values)), 3),
        'sum': sum(values)
    }

elapsed_times: Dict[str,Dict[str, float]] = dict()
llmcalls_and_tokens: Dict[str,Dict] = dict()
for pack_name, questions, gold_answers in question_packs:
    print(pack_name)

    pack_tmp_answers_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_answers_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_answer_dumps = os.listdir(pack_tmp_answers_dir)

    accum_answers: Dict[str,Dict[str, str]] = dict()
    elapsed_times[pack_name] = {'per_question': []}
    llmcalls_and_tokens[pack_name] = {'per_question': []}
    for tmp_dump in tqdm(tmp_answer_dumps):
        answer_info = joblib.load(f"{pack_tmp_answers_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])
        accum_answers[answer_num] = {
            'question': questions[answer_num],
            'gold_answer': gold_answers[answer_num],
            'gen_answer': answer_info['answer']
        }

        elapsed_times[pack_name]['per_question'].append(
            answer_info['elapsed_time'])
        llmcalls_and_tokens[pack_name]['per_question'].append({
            'ollama_requests': answer_info['ollama_requests'],
            'ollama_prompt_tokens': answer_info['ollama_prompt_tokens'],
            'ollama_completion_toknes': answer_info['ollama_completion_toknes']
        })

    elapsed_times[pack_name]['stats'] = calculate_statistics(elapsed_times[pack_name]['per_question'])
    
    llmcalls_and_tokens[pack_name]['stats_ollama_requests'] = calculate_statistics(
        [item['ollama_requests'] for item in llmcalls_and_tokens[pack_name]['per_question']])
    llmcalls_and_tokens[pack_name]['stats_ollama_prompt_tokens'] = calculate_statistics(
            [item['ollama_prompt_tokens'] for item in llmcalls_and_tokens[pack_name]['per_question']])
    llmcalls_and_tokens[pack_name]['stats_ollama_completion_toknes'] = calculate_statistics(
            [item['ollama_completion_toknes'] for item in llmcalls_and_tokens[pack_name]['per_question']])
        

    answers_pack_path = f"{GENERATED_ANSWERS_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_answers, indent=1, ensure_ascii=False))

with open(QA_ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))

with open(QA_LLMCALLS_AND_TOKENS_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(llmcalls_and_tokens, indent=1, ensure_ascii=False))


print("############ DONE ############")
