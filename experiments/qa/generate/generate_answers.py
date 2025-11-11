print("Start QA-pipeline inferencing...")
import sys
import yaml
import joblib
from typing import List, Tuple, Dict
from pprint import pprint
import os
import numpy as np
import pandas as pd
from time import time
from tqdm import tqdm
import json

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
SPEC_ENV_PATH = f"{CONTAINER_ENV_PATH}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.kg_model import KnowledgeGraphModel
from src.pipelines.qa import QAPipeline

####################################################
print("2. Setting paths")

# EXP PATHS
EXPS_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXP_RESULTS_DIR = f"{EXPS_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

CONFIGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['configs_name']}"
QA_CONFIG_PATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qa_config']}"

QA_DATASET_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{SPECEXP_PARAMS['DATASET_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_gen_answers_name']}"
GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

QA_ELAPSED_TIME_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"
AGENT_STAT_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['agent_stat']}"
CACHE_STAT_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['cache_stat']}"

# KG PATHS
DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPECEXP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"
CACHE_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kvdriver_cache_config']}"
INFSTAT_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['inference_stat_config']}"

####################################################
print("3. Loading configs")

kgmodel_config = joblib.load(KG_MODEL_CONFIG_PATH)
kvdriver_config = joblib.load(CACHE_CONFIG_PATH)
llmstat_config = joblib.load(INFSTAT_CONFIG_PATH)

print("KG MODEL_CONFIG:")
pprint(kgmodel_config)
print("KVCACHE CONFIG:")
pprint(kvdriver_config)
print("LLMSTAT CONFIG:")
pprint(llmstat_config)

####################################################
print("4. Setting KG Model")

kg_model = KnowledgeGraphModel(kgmodel_config, kvdriver_config)
print("kg_model:")
pprint(kg_model.count_items(detailed=True))

####################################################
print("5. Setting QA pipeline")

qa_config = joblib.load(QA_CONFIG_PATH)
print("QA-CONFIG:")
pprint(qa_config)

qa_pipeline = QAPipeline(kg_model, qa_config, kvdriver_config, llmstat_config)

print("llmstat cache:")
# qa_pipeline.clear_agent_tgen_stat() # !!! PAY ATTENTION !!!
pprint(qa_pipeline.get_agent_tgen_stat())

print("kv cache: ")
# qa_pipeline.clear_kv_caches( # !!! PAY ATTENTION !!!
#     clear_traversal_cache = False,
#     clear_retrieval_cache = False
# )
pprint(qa_pipeline.get_cache_stat())

####################################################
print("6. Loading QA-dataset")

def diaasqa_qa_load(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    eval_dir_path = f"{dataset_path}/qa_eval"
    pack_files = os.listdir(eval_dir_path)
    packs = []

    for pack_f in pack_files:
        with open(f"{eval_dir_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        questions = list(map(lambda item: item['question'], data))
        answers = list(map(lambda item: item['answer'], data))

        max_samples = SPECEXP_PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']
        if (max_samples > 0):
            questions = questions[:max_samples]
            answers = answers[:max_samples]

        packs.append((pack_name, questions, answers))

    return packs

def hotpotqa_distractor_validation_qa_load(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = SPECEXP_PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def trivia_qa_rcwikipedia_validation_qa_load(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = SPECEXP_PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def rubqdev_qa_load(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = SPECEXP_PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

CUSTOM_LOAD_FUNCS = {
    'diaasq': diaasqa_qa_load,
    'rubq_dev': rubqdev_qa_load,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_qa_load,
    'trivia_qa_rcwikipedia_validation': trivia_qa_rcwikipedia_validation_qa_load
}

question_packs = CUSTOM_LOAD_FUNCS[SPECEXP_PARAMS['DATASET_NAME']](QA_DATASET_PATH)

####################################################
print("7. Start inferencing")

for pack_name, questions, _ in question_packs:

    pack_tmp_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    process = tqdm(range(len(questions)))
    for i in process:
        process.set_postfix_str(pack_name)

        s_time = time()
        answer, info = qa_pipeline.answer(questions[i])
        e_time = time()

        answer_dump_file = f"{pack_tmp_dir}/answer_{i}"
        joblib.dump({'answer': answer, 'info': info,
                    'elapsed_time': e_time - s_time}, answer_dump_file)

####################################################
print("8. Accumulating generated answers")

elapsed_times: Dict[str,Dict[str, float]] = dict()
for pack_name, questions, gold_answers in question_packs:
    print(pack_name)

    pack_tmp_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_answer_dumps = os.listdir(pack_tmp_dir)

    accum_answers: Dict[str,Dict[str, str]] = dict()
    elapsed_times[pack_name] = {'per_question': []}
    for tmp_dump in tqdm(tmp_answer_dumps):
        answer_info = joblib.load(f"{pack_tmp_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])
        accum_answers[answer_num] = {
            'question': questions[answer_num],
            'gold_answer': gold_answers[answer_num],
            'gen_answer': answer_info['answer']
        }

        elapsed_times[pack_name]['per_question'].append(
            answer_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(
        elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['mean'] = np.mean(
        elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['median'] = np.median(
        elapsed_times[pack_name]['per_question'])

    answers_pack_path = f"{GENERATED_ANSWERS_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_answers, indent=1, ensure_ascii=False))

with open(QA_ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))

####################################################
print("9. Saving Cache Info")

print("agent stats after qa-inferencing:")
agent_stats = qa_pipeline.get_agent_tgen_stat()
pprint(agent_stats)
with open(AGENT_STAT_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(agent_stats, indent=1, ensure_ascii=False))

print("cache stat after qa-inferencing:")
cache_stats = qa_pipeline.get_cache_stat()
pprint(cache_stats)
with open(CACHE_STAT_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(cache_stats, indent=1, ensure_ascii=False))

# qa_pipeline.clear_agent_tgen_stat() # !!! PAY ATTENTION !!!
# qa_pipeline.clear_kv_caches( # !!! PAY ATTENTION !!!
#     clear_traversal_cache = False,
#     clear_retrieval_cache = False
# )

print("############ DONE ############")
