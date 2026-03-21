print("Scoring generated answers with base metrics")
import sys
import yaml
import os
import json
import numpy as np
from typing import Dict
import torch
import gc
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

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"
METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['metrics_name']}"

EXP_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
ENCODER_MODEL_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}/{EVAL_PARAMS['bertscore_model_path']}"
METEOR_METRIC_PATH = f"{EXP_DIR}/../../{EVAL_PARAMS['meteor_path']}"
EM_METRIC_PATH = f"{EXP_DIR}/../../{EVAL_PARAMS['exactmatch_path']}"

SETTINGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
EVAL_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['eval']}"

BASEMETRICS_SOURCE_PATH = f"{EXP_DIR}/../../{EVAL_PARAMS['basemetrics_path']}/../.."
sys.path.insert(0, BASEMETRICS_SOURCE_PATH)

from metrics.base_metrics import ReaderMetrics

####################################################
print("3. Setting Metrics-class")

def loading_generated_pack(base_dir: str, pack_name) -> Dict[int, str]:
    with open(f"{base_dir}/{pack_name}", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data


def round5(number: float) -> float:
    return round(number, 5)


def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(f"{save_path}", 'w', encoding='utf-8') as fd:
        fd.write(dump)


METRICS = ReaderMetrics(
    model_path=ENCODER_MODEL_PATH, meteor_filep=METEOR_METRIC_PATH,
    em_filep=EM_METRIC_PATH
)

####################################################
print("4. Evaluating answers")

#
gen_pack_names = os.listdir(GENERATED_ANSWERS_DIR)
for pack_name in gen_pack_names:

    torch.cuda.empty_cache()
    gc.collect()

    generated_pack = loading_generated_pack(GENERATED_ANSWERS_DIR, pack_name)

    generated_answers, filtered_target_answers = [], []
    none_answers = 0
    for i, sample in generated_pack.items():
        if sample['gen_answer'] is not None:
            generated_answers.append(sample['gen_answer'])
            filtered_target_answers.append(sample['gold_answer'])
        else:
            none_answers += 1

    if len(generated_answers) > 0:
        print("Calculating BLEU1...")
        b1_scores = round5(np.mean(METRICS.bleu1(
            generated_answers, filtered_target_answers)))

        print("Calculating BLEU2...")
        b2_scores = round5(np.mean(METRICS.bleu2(
            generated_answers, filtered_target_answers)))

        print("Calculating RougeL...")
        rl_scores = round5(np.mean(METRICS.rougel(
            generated_answers, filtered_target_answers)))

        print("Calculating Meteor...")
        m_scores = round5(np.mean(METRICS.meteor(
            generated_answers, filtered_target_answers)))

        print("Calculating ExactMatch...")
        em_scores = round5(np.mean(METRICS.exact_match(
            generated_answers, filtered_target_answers)))

        print("Calculating F1...")
        f1_scores = round5(np.mean(METRICS.f1(
            generated_answers, filtered_target_answers)))

        # print("Calculating BertScore...")
        # bs_scores = METRICS.bertscore(
        #     generated_answers, filtered_target_answers)

        print("Calculating 'NoAnswer'-score...")
        noansw_scores = sum(list(map(lambda gen_answer: gen_answer.strip(
        ) == EVAL_PARAMS['no_answer'], generated_answers))) / len(generated_answers)

    else:
        b1_scores, b2_scores, rl_scores, m_scores, em_scores, f1_scores, bs_scores, noansw_scores = 0, 0, 0, 0, 0, 0, 0, 0

    none_score = round5(none_answers / len(generated_pack))

    scores = {
        'BLEU1': float(b1_scores),
        'BLEU2': float(b2_scores),
        'METEOR': float(m_scores),
        'RougeL': float(rl_scores),
        'ExactMatch': float(em_scores),
        'F1': float(f1_scores),
        #'BertScore': bs_scores,
        'NoneScore': float(none_score),
        'NoAnswerScore': float(noansw_scores)
    }

    # сохраняем скоры по папку
    save_json(scores, f"{METRICS_DIR}/{pack_name}")

####################################################
print("5. Saving eval params")

with open(EVAL_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EVAL_PARAMS, fd, default_flow_style=False, sort_keys=False)

print("############ DONE ############")
