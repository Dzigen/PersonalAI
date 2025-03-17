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

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

sys.path.insert(0, PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.agents import AgentDriverConfig
from src.agents.utils import AgentConnectorConfig

sys.path.insert(0, f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['QA_EVALUATION']['llm_as_a_judge_path']}")
from llm_as_a_judge.AnswersJudge import AnswersJudgeConfig, AnswersJudge
from llm_as_a_judge import AgentLLMJudgeTaskConfigSelector

################LOADING_HYPERPARAMETERS###################

DS_EXPERIMENT_DIR = f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['EXPERIMENT_NAME']}"

GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['gen_answers_name']}"

TMP_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['tmp_judges_name']}"
METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['judges_name']}"

################ cache driver config ################

if PARAMS['QA_EVALUATION']['judge_llm_config']['caching']:
    kvdriver_config = KeyValueDriverConfig(
        db_vendor='mixed_kv',
        db_config=KVDBConnectionConfig(
            need_to_clear=PARAMS['QA_EVALUATION']['judge_llm_config']['cache_need_to_clear'],
            db_info=PARAMS['QA_EVALUATION']['judge_llm_config']['cache_db_info'],
            params={
                'redis_config': KVDBConnectionConfig(
                    host=PARAMS['BASE_KGR_CONFIG']['ram_cache_config']['host'],
                    port=PARAMS['BASE_KGR_CONFIG']['ram_cache_config']['port'],
                    params=PARAMS['BASE_KGR_CONFIG']['ram_cache_config']['params']),
                'mongo_config': KVDBConnectionConfig(
                    host=PARAMS['BASE_KGR_CONFIG']['persistent_cache_config']['host'],
                    port=PARAMS['BASE_KGR_CONFIG']['persistent_cache_config']['port'],
                    params=PARAMS['BASE_KGR_CONFIG']['persistent_cache_config']['params'])}))

else:
    kvdriver_config = None

############### INITING JUDGE ####################

adriver_config = AgentDriverConfig(
    name=PARAMS['QA_EVALUATION']['judge_llm_config']['agent_config']['vendor'],
    agent_config=AgentConnectorConfig(
        gen_strategy=PARAMS['QA_EVALUATION']['judge_llm_config']['agent_config']['gen_strategy'],
        credentials=PARAMS['QA_EVALUATION']['judge_llm_config']['agent_config']['credentials'],
        ext_params=PARAMS['QA_EVALUATION']['judge_llm_config']['agent_config']['ext_params']))

judge_config = AnswersJudgeConfig(
    lang=PARAMS['QA_EVALUATION']['judge_llm_config']['lang'],
    adriver_config=adriver_config,
    llmjudge_task_config=AgentLLMJudgeTaskConfigSelector.select(
        base_config_version=PARAMS['QA_EVALUATION']['judge_llm_config']['prompts_version']))

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

################# START JUDGING ##################

answers_pack_names = os.listdir(GENERATED_ANSWERS_DIR)
for pack_name in answers_pack_names:
    answers_info = load_json(f"{GENERATED_ANSWERS_DIR}/{pack_name}")

    pack_tmp_dir = f"{TMP_METRICS_DIR}/{pack_name.split('.')[0]}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    process = tqdm(answers_info.items())
    for a_idx, a_info in process:
        process.set_postfix_str(pack_name)
        s_time = time()
        score, info = judge.perform(a_info['question'], a_info['gold_answer'], a_info['gen_answer'])
        e_time = time()

        llmj_dump_file = f"{pack_tmp_dir}/judge_{a_idx}"
        joblib.dump({'judge_score': score,
            'info': info, 'elapsed_time': e_time - s_time},
            llmj_dump_file)

################# ACCUMULATE SCORES ################

judges_pack_names = os.listdir(TMP_METRICS_DIR)
for pack_name in judges_pack_names:
    print(pack_name)

    pack_tmp_dir = f"{TMP_METRICS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_score_dumps = os.listdir(pack_tmp_dir)
    accum_score = {
        'score': dict(), 'elapsed_time': dict(),
        'answer_score_map': dict(), 'answer_time_map': dict()}

    for tmp_dump in tqdm(tmp_score_dumps):
        answer_info = joblib.load(f"{pack_tmp_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])

        accum_score['answer_time_map'][answer_num] = answer_info['elapsed_time']
        accum_score['answer_score_map'][answer_num] = answer_info['judge_score']

    accum_score['elapsed_time']['sum'] = sum(list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['mean'] = np.mean(list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['median'] = np.median(list(accum_score['answer_time_map'].values()))

    filtered_scores = list(filter(lambda score: score is not None, list(accum_score['answer_score_map'].values())))
    accum_score['score']['mean'] = np.mean(filtered_scores)
    accum_score['score']['median'] = np.median(filtered_scores)

    accum_score['score']['frequency'] = dict(Counter(list(accum_score['answer_score_map'].values())))

    save_json(accum_score, f"{METRICS_DIR}/{pack_name}.json")

print("############ DONE ############")
