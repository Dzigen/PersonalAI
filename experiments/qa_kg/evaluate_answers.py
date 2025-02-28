import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
import joblib
from time import time
from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
from evaluate import load
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance
from typing import Dict
from datasets import load_from_disk
import torch
import gc
import os

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

import nltk
nltk.download('wordnet')

################LOADING_HYPERPARAMETERS###################

EXPERIMENTS_DIR_PATH = f"{BASEDIR}/experiments/qa_kg"
PARAMS_FILE_PATH = f"{EXPERIMENTS_DIR_PATH}/params.yaml"

# Read YAML file
with open(PARAMS_FILE_PATH, 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

BASE_PATH = f"{BASEDIR}/data/knowledge_graphs/"
DATASET_PATH = BASE_PATH + f"{HYPER_PARAMS['dataset_name']}/"
KG_PATH = DATASET_PATH + f"{HYPER_PARAMS['kg_name']}/"

GRAPH_DRIVER_CONFIG_PATH = KG_PATH + "graph_config"
EMBEDDINGS_DRIVER_CONFIG_PATH = KG_PATH + "embeddings_config"

EXPERIMENT_DIR = f"{EXPERIMENTS_DIR_PATH}/{HYPER_PARAMS['dataset_name']}/exp_logs/{HYPER_PARAMS['experiment_name']}"
GENERATED_ANSWERS_DIR = f'{EXPERIMENT_DIR}/answer_packs'
METRICS_DIR = f'{EXPERIMENT_DIR}/metric_packs'

TMP_GENERATED_ANSWERS_DIR = f'{EXPERIMENT_DIR}/tmp_answer_packs'

QA_ELAPSED_TIME = f'{EXPERIMENT_DIR}/elapsed_time.json'

HYPERPARAMS_SAVE_PATH = f'{EXPERIMENT_DIR}/hyperparams.json'
QA_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/qa_config'
RETRIEVER_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/retirver_config'
FILTER_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/filter_config'

####################################################

# Source: https://amitness.com/2020/08/information-retrieval-evaluation/

#Retrieval metrics
# - mAP
# - MRR
# - precision
# - recall
# - f1
#Reader metrics
# - BLEU presision
# - ROUGE recall
# - METEOR f1

from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
from evaluate import load
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance

class ReaderMetrics:
    def __init__(self, model_path, base_dir = '../..'):
        self.rouge_obj = ROUGEScore()
        self.bleu1_obj = BLEUScore(n_gram=1)
        self.bleu2_obj = BLEUScore(n_gram=2)
        print("Loading Meteor...")
        self.meteor_obj = evaluate.load("./metrics/meteor")
        print("Loading ExactMatch")
        self.em_obj = evaluate.load("./metrics/exact_match")
        self.bertscore_obj = BERTScore(f"{base_dir}/models/{model_path}", return_hash=True)

    def bertscore(self, predicted: List[str], targets: List[str]):
        output = self.bertscore_obj(predicted, targets)
        output['precision'] = round(float(output['precision'].mean()), 5)
        output['recall'] = round(float(output['recall'].mean()), 5)
        output['f1'] = round(float(output['f1'].mean()), 5)

        return output

    def rougel(self, predicted: List[str], targets: List[str]):
        return [self.rouge_obj(
            predicted[i], targets[i])['rougeL_fmeasure']
                 for i in range(len(targets))]

    def bleu1(self, predicted: List[str], targets: List[str]):
        return [self.bleu1_obj(
            [predicted[i]], [[targets[i]]])
                 for i in range(len(targets))]

    def bleu2(self, predicted: List[str], targets: List[str]):
        return [self.bleu2_obj(
            [predicted[i]], [[targets[i]]])
                 for i in range(len(targets))]

    def meteor(self, predicted: List[str], targets: List[str]):
        return [self.meteor_obj.compute(
            predictions=[predicted[i]], references=[targets[i]])['meteor']
                 for i in range(len(targets))]

    def exact_match(self, predicted: List[str], targets: List[str]):
        return [self.em_obj.compute(
            predictions=[predicted[i]], references=[targets[i]], ignore_case=True, ignore_punctuation=True)["exact_match"]
                for i in range(len(targets))]

    def levenshtain_score(self, predicted: List[str], targets: List[str]):
        return list(map(lambda pair: levenshtain_distance(pair[1], pair[0]), zip(predicted, targets)))

####################################################

def loading_generated_pack(base_dir: str, pack_name) -> Dict[int,str]:
    with open(f"{base_dir}/{pack_name}.json", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data

def round5(number: float) -> float:
    return round(number, 5)

def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(f"{save_path}.json", 'w', encoding='utf-8') as fd:
        fd.write(dump)

METRICS = ReaderMetrics(base_dir="../..", model_path=HYPER_PARAMS['eval_bs_model'])

####################################################

def diaasqa_aload(dataset_path: str) -> List[List[str, List[str]]]:
    pack_files = os.listdir(dataset_path)
    packs = []

    for pack_f in pack_files:
        with open(f"{dataset_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        answers = list(map(lambda item: item['answer'], data))

        packs.append((pack_name, answers))

    return packs

def hotpotqa_distractor_validation_aload(dataset_path: str) -> List[List[str, List[str]]]:
    dataset = load_from_disk(dataset_path)
    return dataset['answer']

CUSTOM_LOAD_FUNCS = {
    'diaasqa': diaasqa_aload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_aload
}

# загружаем датасте
answers_packs = CUSTOM_LOAD_FUNCS[HYPER_PARAMS['dataset_name']](HYPER_PARAMS['eval_dataset_path'])

####################################################

#
for pack_name, all_target_answers in tqdm(answers_packs):

    torch.cuda.empty_cache()
    gc.collect()

    generated_pack = loading_generated_pack(GENERATED_ANSWERS_DIR, pack_name)

    filtered_target_answers = []
    generated_answers = []
    none_answers = 0
    for i, answer in generated_pack.items():
        if answer is not None:
            generated_answers.append(answer)
            filtered_target_answers.append(all_target_answers[int(i)])
        else:
            none_answers += 1

    if len(generated_answers) > 0:
        b1_scores = round5(np.mean(METRICS.bleu1(generated_answers, filtered_target_answers)))
        b2_scores  = round5(np.mean(METRICS.bleu2(generated_answers, filtered_target_answers)))
        rl_scores = round5(np.mean(METRICS.rougel(generated_answers, filtered_target_answers)))
        m_scores = round5(np.mean(METRICS.meteor(generated_answers, filtered_target_answers)))
        em_scores = round5(np.mean(METRICS.exact_match(generated_answers, filtered_target_answers)))
        bs_scores = METRICS.bertscore(generated_answers, filtered_target_answers)
    else:
        b1_scores, b2_scores, rl_scores, m_scores, em_scores, bs_scores = 0,0,0,0,0,0

    none_score = round5(none_answers / len(generated_pack))

    scores = {
        'BLEU1': float(b1_scores),
        'BLEU2': float(b2_scores),
        'METEOR': float(m_scores),
        'RougeL': float(rl_scores),
        'ExactMatch': float(em_scores),
        'BertScore': bs_scores,
        'BertScore_model': HYPER_PARAMS['eval_bs_model'],
        'NoneScore': float(none_score)
    }

    # сохраняем скоры по папку
    save_json(scores, f"{METRICS_DIR}/{pack_name}")
