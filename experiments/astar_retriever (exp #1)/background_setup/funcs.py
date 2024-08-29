import json
import requests
from langchain_huggingface import HuggingFaceEmbeddings
import os
from typing import List, Dict, Tuple
import hashlib
from time import sleep, time
from tqdm import tqdm
from collections import Counter
import numpy as np
import gc
import torch
import joblib
import chromadb
from scipy.spatial import distance

PROMPT_QA_TEMPLATE = """Answer the question, based on provided info by analogy with examples given. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ...
Question 1: Whose opinions from Anthony and Grace about devices are most similar to Faith's?
Info 1: person: Anthony, device: Xiaomi, opinion: hard, feature: maintenance point
person: Anthony, device: mate30pro, opinion: not as good as, feature: signal
person: Anthony, device: iPhone, opinion: not as good as, feature: signal
person: Grace, device: Xiaomi 12, opinion: beat, feature: charging speed
person: Faith, device: Xiaomi, opinion: problem, feature: product control
person: Faith, device: k30s, opinion: not as good, feature: film effect
person: Faith, device: red rice, opinion: not as good, feature: film effect
### Answer 1
Chain of thought 1: The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat," which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good."
Final answer 1: Anthony
Question 2: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
Info 2: person: Alejandro, time: 15.11.2020, opinion: beats, device: Apple, feature: battery life
person: Jacqueline, time: 30.12.2020, opinion: Nice pictures taken, device: Apple, feature: taking pictures
person: Diego, time: 30.12.2020, opinion: Doesnt overheat, device: Apple, feature: heat radiation
person: Lily, time: 30.12.2020, opinion: Not bad, device: Apple, feature: configuration of other processors
person: Margaret, time: 25.11.2020, opinion: Pictures turn blurry, device: Apple, feature: taking pictures
person: Amber, time: 25.11.2020, opinion: Really unhelpful, device: Apple, feature: sales
person: Jessica, time: 25.11.2020, opinion: Always been strong, device: Apple, feature: signal
person: Bernard, time: 25.11.2020, opinion: No lag, device: Apple, feature: play games
### Answer 2
Chain of thought 2: To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. From the provided info, only Jessica's opinion mentions the signal: "Always been strong." This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.
Final answer 2: Positive
Question 3: {q}
Info 3: {c}
### Answer 3 """

# CHANGE TO ABSOLUTE PATH TO DIRS #
LOG_DIR = "./logs"
UTILS_DIR = './utils'
EVAL_DATADIR = "./qa_eval"
# CHANGE TO ABSOLUTE PATH TO DITS #

SAVE_STAGE3_1_LOGDIR = f"{LOG_DIR}/stage3_1"
SAVE_STAGE4_LOGDIR = f"{LOG_DIR}/stage4"
SAVE_SCORES_LOGDIR = f"{LOG_DIR}/final"

LOG_TMPDATA_DIRNAME = "tmp"
LOG_STATSDATA_DIRNAME = "stats"
LOG_META_FILENMAE = "metadata.json"
LOG_SCORES_DIRNAME = 'scores'

LLM_URL = "https://985f-109-252-76-222.ngrok-free.app/llama" 

def generate(prompt: str) -> str:
    flag = True
    while flag:    
        try:
            response = requests.post(LLM_URL, params = {"prompt": prompt})
            resp = response.json()["response"]
            flag = False
        except (requests.ConnectionError, requests.ReadTimeout) as e:
            print("Connection error: ", str(e))
            sleep(1)

    return resp

def check_create_dir(new_dir_path: str):
    if os.path.exists(new_dir_path):
        print("Директория существует")
        raise ValueError
    else:
        os.mkdir(new_dir_path)

def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(save_path, 'w', encoding='utf-8') as fd:
        fd.write(dump)

def load_json(load_path: str) -> Dict[str,object]:
    with open(load_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data

def round5(number: float) -> float:
    return round(number, 5)

###############

def preproc_tripletes(raw_triplets: List[List[str]], META) -> str:
    formated_triplets = []

    if len(raw_triplets) == 0:
        return "empty."

    for triplete in raw_triplets:
        #print(len(triplete))

        if triplete[1]["type"] == "manufacturer":
            device_node, company_node = (triplete[0], triplete[2]) if 'device' in triplete[0]["labels"] else (triplete[2], triplete[0])
            formated_triplete = META["TRPLETE_PROMPT_TEMPLATES"]["manufacturer"].format(d=device_node['name'], c=company_node['name'])

        elif triplete[1]["type"] == "opinion":
            device_node, feature_node = (triplete[0], triplete[2]) if 'device' in triplete[0]["labels"] else (triplete[2], triplete[0])
            relation = triplete[1]
            formated_triplete = META["TRPLETE_PROMPT_TEMPLATES"]["opinion"].format(
                p=relation["person"], o=relation["opinion"].replace('_', ' '),
                t=relation["time"], f=feature_node['name'],d=device_node['name'])
        
        elif triplete[1]["type"] == "has_device":
            device_node, person_node = (triplete[0], triplete[2]) if 'device' in triplete[0]["labels"] else (triplete[2], triplete[0])
            formated_triplete = META["TRPLETE_PROMPT_TEMPLATES"]['has_device'].format(d=device_node['name'], p=person_node['name'])

        else:
            raise ValueError
        
        formated_triplets.append(formated_triplete)

    str_triplets = "\n".join(formated_triplets[:META["MAX_LIST_LEN"]] if META["MAX_LIST_LEN"] > 0 else formated_triplets)
    return str_triplets

def generate_answers_from_triplets_file(qa_file: str, load_log_tmpdata_dir: str, save_log_tmpdata_dir: str, META: Dict, EVAL_DATADIR: str):
    print(qa_file)
    triplets_data = load_json(f"{load_log_tmpdata_dir}/{qa_file}")[:1]
    questions_data = load_json(f"{EVAL_DATADIR}/{qa_file}")

    generated_answers = []
    for triplete_item, quiestion_item in tqdm(zip(triplets_data, questions_data)):
        context = preproc_tripletes(triplete_item['filtered_triplets'], META)
        question = quiestion_item['question']
        prompt = META["QUESTION_PROMPT_TEMPLATE"].format(q=question, c=context)
        
        #print()
        #print(prompt)
        
        found_line = ""
        raw_answer = generate(prompt).strip()
        for line in raw_answer.split("\n"):
            if "Final answer 3" in line:
                found_line = line
                break
        if found_line:
            answer = found_line.split("Final answer 3: ")[-1]
        else:
            answer = raw_answer.split("\n")[1]

        #print(answer)

        generated_answers.append({'generated_answer': answer, 'used_prompt': prompt})
        
    save_json(generated_answers, f"{save_log_tmpdata_dir}/{qa_file}")

##############

def measure_quality_from_answers_file(qa_file: str, gen_answers_dir: str, save_log_tmpdata_dir: str, EVAL_DATADIR, METRICS):
    print(qa_file)
    generated_answers_data = load_json(f"{gen_answers_dir}/{qa_file}")
    target_answers_data = load_json(f"{EVAL_DATADIR}/{qa_file}")
    
    gen_answers = list(map(lambda item: item['generated_answer'], generated_answers_data)) 
    trgt_answers = list(map(lambda item: item['answer'], target_answers_data))[:len(gen_answers)]

    b1_scores = METRICS.bleu1(gen_answers, trgt_answers)
    b2_scores  = METRICS.bleu2(gen_answers, trgt_answers)
    rl_scores = METRICS.rougel(gen_answers, trgt_answers)
    m_scores = METRICS.meteor(gen_answers, trgt_answers)
    em_scores = METRICS.exact_match(gen_answers, trgt_answers)

    scores = {
        'BLEU1': str(round5(np.mean(b1_scores))),
        'BLEU2': str(round5(np.mean(b2_scores))),
        'METEOR': str(round5(np.mean(m_scores))),
        'RougeL': str(round5(np.mean(rl_scores))),
        'ExactMatch': str(round5(np.mean(em_scores)))
    }

    save_json(scores, f"{save_log_tmpdata_dir}/{qa_file}")