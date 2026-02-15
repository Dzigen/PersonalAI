print("Scoring retrieved triples with llm-as-a-judge")

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
LLMASAJUDGE_SOURCE_PATH = f"{WORKSPACE_CONTAINER_PATH}/{EVAL_PARAMS['llm_as_a_judge_path']}/.."
sys.path.insert(0, LLMASAJUDGE_SOURCE_PATH)

from llm_as_a_judge_mine import MINEJudgeConfig, MINEJudge

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['retrieved_triples_name']}"

TMP_JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_judges_name']}"
JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"

SETTINGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
EVAL_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['eval']}"

####################################################
print("3. Setting Judge")

judge_config = MINEJudgeConfig(
    model=EVAL_PARAMS['judge_llm_config']['credentials']['model'],
    host=EVAL_PARAMS['judge_llm_config']['credentials']['host'],
    port=EVAL_PARAMS['judge_llm_config']['credentials']['port'],
    gen_strategy = EVAL_PARAMS['judge_llm_config']['gen_strategy']
)

judge = MINEJudge(judge_config)

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
print("4. Start scoring retrieved triples with Judge")

triples_pack_names = os.listdir(RETRIEVED_TRIPLES_DIR)
for pack_name in triples_pack_names:
    triples_info = load_json(f"{RETRIEVED_TRIPLES_DIR}/{pack_name}")

    pack_tmp_dir = f"{TMP_JUDGES_DIR}/{pack_name.split('.')[0]}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    process = tqdm(triples_info.items())
    for t_idx, t_info in process:
        process.set_postfix_str(pack_name)

        formated_context = "\n".join(list(lambda str_triple: f"- {str_triple}", t_info['retrieved_triples']))

        s_time = time()
        score = judge.perform(t_info['query'], formated_context)
        e_time = time()

        llmj_dump_file = f"{pack_tmp_dir}/judge_{t_idx}"
        llmj_result = {'judge_score': score, 'elapsed_time': e_time - s_time}
        joblib.dump(llmj_result, llmj_dump_file)

####################################################
print("5. Accumulating Judge scores")

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
print("6. Saving eval params")

with open(EVAL_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EVAL_PARAMS, fd, default_flow_style=False, sort_keys=False)

print("############ DONE ############")
