import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
import joblib
from time import time
from typing import List, Dict, Tuple
import pandas as pd

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

###################################

sys.path.insert(0, PARAMS['BASE_PERSONALAI_DIR'])

from src.kg_model import KnowledgeGraphModel
from src.pipelines.qa import QAPipelineConfig, QAPipeline
from src.pipelines.qa.kg_reasoning import KnowledgeGraphReasonerConfig

################LOADING_HYPERPARAMETERS###################

KG_DIR_PATH = f"{PARAMS['KGS_BASE_PATH']}/{PARAMS['DATASET_NAME']}/{PARAMS['KNOWLEDGE_GRAPH_NAME']}"
GRAPH_DRIVER_CONFIG_PATH = f"{KG_DIR_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['graph_config']}"
EMBEDDINGS_DRIVER_CONFIG_PATH = f"{KG_DIR_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['embeddings_config']}"

MEM_PARAMS_FILEP = f"{KG_DIR_PATH}/{PARAMS['MEM_PIPELINE_HYPERP']}"
with open(MEM_PARAMS_FILEP, 'r') as stream:
    MEM_PARAMS = yaml.safe_load(stream)

DS_EXPERIMENT_DIR = f"{PARAMS['EXPERIMENTS_BASE_DIR']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['KNOWLEDGE_GRAPH_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['tmp_gen_answers_name']}'
GENERATED_ANSWERS_DIR = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['gen_answers_name']}'
METRICS_DIR = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['metrics_name']}'
KG_REASONER_CONFIG_PATH = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_FILES_NAMES']['kg_reasoner_config']}'

QA_ELAPSED_TIME_SPATH = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_FILES_NAMES']['elapsed_time']}'
HYPERPARAMS_SPATH = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_FILES_NAMES']['hyperparameters']}'
QA_CONFIG_SPATH = f'{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_FILES_NAMES']['qapipeline_config']}'

###################################

# инициализируем граф знаний

graph_config = joblib.load(GRAPH_DRIVER_CONFIG_PATH)
embed_config = joblib.load(EMBEDDINGS_DRIVER_CONFIG_PATH)

# !!! IMPORTANT !!!
graph_config.driver_config.db_config.need_to_clear = False
embed_config.nodesdb_driver_config.db_config.need_to_clear = False
embed_config.tripletsdb_driver_config.db_config.need_to_clear = False
# !!! IMPORTANT !!!

print("graph_config:", graph_config)
print("embed_config:", embed_config)

kg_model = KnowledgeGraphModel(
    graph_config=graph_config,
    embeddings_config=embed_config)

print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

###############INITING QA-PIPELINE####################

kg_reasoner_config = joblib.load(KG_REASONER_CONFIG_PATH)

print("KG_REASONER-CONFIG:\n", kg_reasoner_config)

qa_config = QAPipelineConfig(
    reasoner_config=KnowledgeGraphReasonerConfig(
        reasoner_name=PARAMS['BASE_KGR_CONFIG']['name'],
        reasoner_hyperparameters=kg_reasoner_config ))

print("KG_PIPELINE-CONFIG:\n", qa_config)

qa_pipeline = QAPipeline(kg_model, qa_config)

############SAVING HYPERPARAMS############

with open(HYPERPARAMS_SPATH, 'w') as fd:
    yaml.dump(PARAMS, fd, default_flow_style=False)

joblib.dump(qa_config, QA_CONFIG_SPATH)

#################LOADING_QUESTIONS##################

def diaasqa_qa_load(dataset_path: str) -> List[List[str, List[str]]]:
    pack_files = os.listdir(f"{dataset_path}/qa_eval")
    packs = []

    for pack_f in pack_files:
        with open(f"{dataset_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        questions = list(map(lambda item: item['question'], data))
        answers = list(map(lambda item: item['answer'], data))

        if (PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack'] > 0):
            questions = questions[:PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']]
            answers = answers[:PARAMS['QA_DATASET_HYPERP']['max_samples_per_pack']]

        packs.append((pack_name, questions, answers))

    return packs


def hotpotqa_distractor_validation_qa_load(dataset_path: str) -> List[List[str, List[str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()
    packs = [['all', questions, answers]]

    return packs

CUSTOM_LOAD_FUNCS = {
    'diaasqa': diaasqa_qa_load,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_qa_load
}

question_packs = CUSTOM_LOAD_FUNCS[PARAMS['DATASET_NAME']](MEM_PARAMS['DATASET_PATH'])

#################START_QA_PROCESS##################

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
        joblib.dump({'answer': answer, 'info': info, 'elapsed_time': e_time - s_time}, answer_dump_file)

#################accumulate generate answers#################

elapsed_times = {}
for pack_name, questions, gold_answers in question_packs:

    pack_tmp_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_answer_dumps = os.listdir(pack_tmp_dir)

    accum_answers = dict()
    elapsed_times[pack_name] = {'per_question': []}
    for tmp_dump in tqdm(tmp_answer_dumps):
        answer_info = joblib.load(f"{pack_tmp_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])
        accum_answers[answer_num] = {
            'question': questions[answer_num],
            'gold_answer': gold_answers[answer_num],
            'gen_answer': answer_info['answer']
        }

        elapsed_times[pack_name]['per_question'].append(answer_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['mean'] = np.mean(elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['median'] = np.median(elapsed_times[pack_name]['per_question'])

    answers_pack_path = f"{GENERATED_ANSWERS_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_answers, indent=1, ensure_ascii=False))

with open(QA_ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))
