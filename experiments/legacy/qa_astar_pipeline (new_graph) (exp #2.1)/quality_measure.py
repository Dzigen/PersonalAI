from src.utils import ReaderMetrics
import sys
import json
from tqdm import tqdm
from typing import Dict
import numpy as np
import torch
import os
from time import time
import gc

import nltk
nltk.download('punkt_tab')
nltk.download('wordnet')

# TO CHANGE
BASEDIR = "/workspace"
# TO CHNAGE

sys.path.insert(0, BASEDIR)

EVAL_DATADIR = '../../data/qa_eval'


###########

save_log_tmpdata_dir = "./logs/scores"
gen_answers_dir = "./logs/generated"

METRICS = ReaderMetrics(
    base_dir="../..", bs_model_path="google/electra-base-discriminator")

###########


def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(save_path, 'w', encoding='utf-8') as fd:
        fd.write(dump)


def load_json(load_path: str) -> Dict[str, object]:
    with open(load_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data


def round5(number: float) -> float:
    return round(number, 5)


def measure_quality_from_answers_file(qa_file: str, gen_answers_dir: str, save_log_tmpdata_dir: str):
    print(qa_file)
    generated_answers_data = load_json(f"{gen_answers_dir}/{qa_file}")
    target_answers_data = load_json(f"{EVAL_DATADIR}/{qa_file}")

    gen_answers = list(
        map(lambda item: item['generated_answer'], generated_answers_data))
    trgt_answers = list(map(lambda item: item['answer'], target_answers_data))[
        :len(gen_answers)]

    b1_scores = METRICS.bleu1(gen_answers, trgt_answers)
    b2_scores = METRICS.bleu2(gen_answers, trgt_answers)
    rl_scores = METRICS.rougel(gen_answers, trgt_answers)
    m_scores = METRICS.meteor(gen_answers, trgt_answers)
    em_scores = METRICS.exact_match(gen_answers, trgt_answers)
    bs_scores = METRICS.bertscore(gen_answers, trgt_answers)

    scores = {
        'BLEU1': str(round5(np.mean(b1_scores))),
        'BLEU2': str(round5(np.mean(b2_scores))),
        'METEOR': str(round5(np.mean(m_scores))),
        'RougeL': str(round5(np.mean(rl_scores))),
        'ExactMatch': str(round5(np.mean(em_scores))),
        'BertScore': {k: str(round5(float(v.mean()))) for k, v in bs_scores.items() if k != 'hash'}
    }

    torch.cuda.empty_cache()
    gc.collect()

    save_json(scores, f"{save_log_tmpdata_dir}/{qa_file}")

###########


generated_files = os.listdir(gen_answers_dir)
for gen_file in generated_files:
    measure_quality_from_answers_file(
        gen_file, gen_answers_dir, save_log_tmpdata_dir)
