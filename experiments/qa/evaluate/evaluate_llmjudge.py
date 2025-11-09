print("Scoring generated answers with llm-as-a-judge")

import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
import joblib
from time import time
import numpy as np
from collections import Counter
from tqdm import tqdm
from typing import Dict
import os

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

# Read YAML file (eval-params)
EVAL_PARAMS_FILEP = sys.orig_argv[4]
with open(EVAL_PARAMS_FILEP, 'r') as stream:
    EVAL_PARAMS = yaml.safe_load(stream)

WORKSPACE_CONTAINER_PATH = EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
sys.path.insert(0, WORKSPACE_CONTAINER_PATH)

LLMASAJUDGE_SOURCE_PATH = f"{WORKSPACE_CONTAINER_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EVAL_PARAMS['llm_as_a_judge_path']}/.."
sys.path.insert(0, LLMASAJUDGE_SOURCE_PATH)

from llm_as_a_judge import AgentLLMJudgeTaskConfigSelector
from llm_as_a_judge.AnswersJudge import AnswersJudgeConfig, AnswersJudge
from src.agents.utils import AgentConnectorConfig
from src.agents import AgentDriverConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

TMP_JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_judges_name']}"
JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"

EXP_DIR = f'{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}'
EVALUATE_DIR = f'{EXP_DIR}/{EXPDIR_PARAMS['llmasajudge_kv_dir']}'

SETTINGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
EVAL_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['eval']}"

####################################################
print("3. Setting Caching mechanism")

llmasajudge_raw_config = EVAL_PARAMS['QA_EVALUATION']['judge_llm_config']

if llmasajudge_raw_config['caching']:
    kvdriver_config = KeyValueDriverConfig(
        db_vendor='inmemory_kv',
        db_config=KVDBConnectionConfig(
            need_to_clear=llmasajudge_raw_config['cache_need_to_clear'],
            db_info=llmasajudge_raw_config['cache_db_info'],
            host='localhost',
            params={
                'load_from_disk': True,
                'load_dump_name': None,
                'load_dump_dir': EVALUATE_DIR,
                'save_on_disk': True,
                'save_dump_dir': EVALUATE_DIR,
                'rewrite': True,
                'max_storage': 5e+8
            }
        )
    )

else:
    kvdriver_config = None

####################################################
print("4. Setting Judge")

adriver_config = AgentDriverConfig(**llmasajudge_raw_config['agent_driver_config'])
adriver_config.formate_fields()

judge_config = AnswersJudgeConfig(
    lang=llmasajudge_raw_config['lang'],
    adriver_config=adriver_config,
    llmjudge_task_config=AgentLLMJudgeTaskConfigSelector.select(
        base_config_version=llmasajudge_raw_config['prompts_version']))

judge = AnswersJudge(judge_config, kvdriver_config)

##################################################

def load_json(load_path: str) -> Dict:
    with open(load_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data

def round5(number: float) -> float:
    return round(number, 5)

def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(f"{save_path}", 'w', encoding='utf-8') as fd:
        fd.write(dump)

####################################################
print("5. Start scoring answers with Judge")

answers_pack_names = os.listdir(GENERATED_ANSWERS_DIR)
for pack_name in answers_pack_names:
    answers_info = load_json(f"{GENERATED_ANSWERS_DIR}/{pack_name}")

    pack_tmp_dir = f"{TMP_JUDGES_DIR}/{pack_name.split('.')[0]}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    process = tqdm(answers_info.items())
    for a_idx, a_info in process:
        process.set_postfix_str(pack_name)
        s_time = time()
        score, info = judge.perform(
            a_info['question'], a_info['gold_answer'], a_info['gen_answer'])
        e_time = time()

        llmj_dump_file = f"{pack_tmp_dir}/judge_{a_idx}"
        llmj_result = {'judge_score': score, 'info': info, 'elapsed_time': e_time - s_time}
        joblib.dump(llmj_result, llmj_dump_file)

####################################################
print("6. Accumulating Judge scores")

judges_pack_names = os.listdir(TMP_JUDGES_DIR)
for pack_name in judges_pack_names:
    print(pack_name)

    pack_tmp_dir = f"{TMP_JUDGES_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_score_dumps = os.listdir(pack_tmp_dir)
    accum_score = {
        'llm-as-a-judge': dict(), 'elapsed_time': dict(),
        'answer_score_map': dict(), 'answer_time_map': dict()}

    for tmp_dump in tqdm(tmp_score_dumps):
        answer_info = joblib.load(f"{pack_tmp_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])

        accum_score['answer_time_map'][answer_num] = answer_info['elapsed_time']
        accum_score['answer_score_map'][answer_num] = answer_info['judge_score']

    accum_score['elapsed_time']['sum'] = sum(
        list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['mean'] = np.mean(
        list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['median'] = np.median(
        list(accum_score['answer_time_map'].values()))

    filtered_scores = list(filter(lambda score: score is not None, list(
        accum_score['answer_score_map'].values())))
    accum_score['llm-as-a-judge']['mean'] = np.mean(filtered_scores)
    accum_score['llm-as-a-judge']['median'] = np.median(filtered_scores)

    accum_score['llm-as-a-judge']['frequency'] = dict(
        Counter(list(accum_score['answer_score_map'].values())))

    save_json(accum_score, f"{JUDGES_DIR}/{pack_name}.json")

####################################################
print("7. Saving eval params")

with open(EVAL_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EVAL_PARAMS, fd, default_flow_style=False)

print("############ DONE ############")
