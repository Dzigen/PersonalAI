import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance
from typing import Dict
import torch
import gc
import os


import nltk
nltk.download('wordnet')

################LOADING_HYPERPARAMETERS###################

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

DS_EXPERIMENT_DIR = f"{PARAMS['EXPERIMENTS_BASE_DIR']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['KNOWLEDGE_GRAPH_NAME']}"

GENERATED_ANSWERS_DIR = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['gen_answers_name']}'
METRICS_DIR = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['metrics_name']}'

####################################################

class ReaderMetrics:
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
    def __init__(self, model_path:str, base_dir:str= '../..',
                 meteor_filep:str="./metrics/meteor",
                 em_filep:str="./metrics/exact_match"):
        self.rouge_obj = ROUGEScore()
        self.bleu1_obj = BLEUScore(n_gram=1)
        self.bleu2_obj = BLEUScore(n_gram=2)
        print("Loading Meteor...")
        self.meteor_obj = evaluate.load(meteor_filep)
        print("Loading ExactMatch")
        self.em_obj = evaluate.load(em_filep)
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

METRICS = ReaderMetrics(
    base_dir=PARAMS['BASE_PERSONALAI_DIR'],
    model_path=PARAMS['EVAL_BERTSCORE_MODEL'],
    meteor_filep=PARAMS['METEOR_METRIC_PATH'],
    em_filep=PARAMS['EXACT_MATCH_PATH'])

####################################################

#
gen_pack_names = os.listdir(GENERATED_ANSWERS_DIR)
process = tqdm(gen_pack_names)
for pack_name in process:

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
        'NoneScore': float(none_score)
    }

    # сохраняем скоры по папку
    save_json(scores, f"{METRICS_DIR}/{pack_name}")
