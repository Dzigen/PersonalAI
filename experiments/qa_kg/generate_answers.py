import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
import joblib
from time import time

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

###################################

from src.kg_model import KnowledgeGraphModel
from src.pipelines.qa import QAPipelineConfig, QAPipeline
from src.pipelines.qa import QueryLLMParserConfig, KnowledgeComparatorConfig, KnowledgeRetrieverConfig, QALLMGeneratorConfig

################LOADING_HYPERPARAMETERS###################

# Read YAML file
with open("params.yaml", 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

BASE_PATH = "../../data/knowledge_graphs/"
DATASET_PATH = BASE_PATH + f"{HYPER_PARAMS['dataset_name']}/"
KG_PATH = DATASET_PATH + f"{HYPER_PARAMS['kg_name']}/"

GRAPH_DRIVER_CONFIG_PATH = KG_PATH + "graph_config"
EMBEDDINGS_DRIVER_CONFIG_PATH = KG_PATH + "embeddings_config"

EXPERIMENT_DIR = f"{HYPER_PARAMS['dataset_name']}/exp_logs/{HYPER_PARAMS['experiment_name']}"
GENERATED_ANSWERS_DIR = f'{EXPERIMENT_DIR}/answer_packs'
METRICS_DIR = f'{EXPERIMENT_DIR}/metric_packs'

TMP_GENERATED_ANSWERS_DIR = f'{EXPERIMENT_DIR}/tmp_answer_packs'

QA_ELAPSED_TIME = f'{EXPERIMENT_DIR}/elapsed_time.json'

HYPERPARAMS_SAVE_PATH = f'{EXPERIMENT_DIR}/hyperparams.json'
QA_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/qa_config'
RETRIEVER_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/retirver_config'
FILTER_CONFIG_SAVE_PATH = f'{EXPERIMENT_DIR}/filter_config'

###################################

# инициализируем граф знаний

graph_config = joblib.load(GRAPH_DRIVER_CONFIG_PATH)
embed_config = joblib.load(EMBEDDINGS_DRIVER_CONFIG_PATH)

# !!! IMPORTANT !!!
graph_config.driver_config.db_config.need_to_clear = False
embed_config.nodesdb_driver_config.db_config.need_to_clear = False
embed_config.tripletsdb_driver_config.db_config.need_to_clear = False
# !!! IMPORTANT !!!

# fixing paths to vector dbs
embed_config.embedder_config.model_name_or_path = '/'.join(embed_config.embedder_config.model_name_or_path.split("/")[1:])
embed_config.nodesdb_driver_config.db_config.path = '/'.join(embed_config.nodesdb_driver_config.db_config.path.split("/")[1:])
embed_config.tripletsdb_driver_config.db_config.path = '/'.join(embed_config.tripletsdb_driver_config.db_config.path.split("/")[1:])

print("graph_config:", graph_config)
print("embed_config:", embed_config)

kg_model = KnowledgeGraphModel(
    graph_config=graph_config,
    embeddings_config=embed_config)

print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

###################################

# задаём конфигурацию qa-пайплайна

retriever_config = joblib.load(HYPER_PARAMS['knowledge_retriever']['retriever_config_path'])
filter_config = joblib.load(HYPER_PARAMS['knowledge_retriever']['filter_config_path'])

print("retriever_config:", retriever_config)
print("filter_config:", filter_config)

qa_config = QAPipelineConfig(
    query_parser_config=QueryLLMParserConfig(lang=HYPER_PARAMS['language']),

    knowledge_comparator_config=KnowledgeComparatorConfig(),

    knowledge_retriever_config=KnowledgeRetrieverConfig(
        retriever_method=HYPER_PARAMS['knowledge_retriever']['retriever_method'], retriever_config=retriever_config,
        filter_method=HYPER_PARAMS['knowledge_retriever']['filter_method'], filter_config=filter_config),

    answer_generator_config=QALLMGeneratorConfig(lang=HYPER_PARAMS['language']))

qa_pipeline = QAPipeline(kg_model, qa_config)

##################STRUCTURE_INITs#################

if HYPER_PARAMS['init_struct']:
    if not os.path.exists(HYPER_PARAMS['dataset_name']):
        raise ValueError("Директории не существует")

    if os.path.exists(EXPERIMENT_DIR):
        raise ValueError("Директория существует")

    if os.path.exists(GENERATED_ANSWERS_DIR):
        raise ValueError("Директория существует")

    if os.path.exists(METRICS_DIR):
        raise ValueError("Директория существует")

    # создать каталог
    os.mkdir(EXPERIMENT_DIR)
    # создать каталог для ответов
    os.mkdir(GENERATED_ANSWERS_DIR)
    # создать каталог для метрик
    os.mkdir(METRICS_DIR)

    os.mkdir(TMP_GENERATED_ANSWERS_DIR)

    # сохранить параметры
    with open(HYPERPARAMS_SAVE_PATH, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(HYPER_PARAMS, indent=1, ensure_ascii=False))

    # сохранить конфиги
    joblib.dump(qa_config, QA_CONFIG_SAVE_PATH)
    joblib.dump(retriever_config, RETRIEVER_CONFIG_SAVE_PATH)
    joblib.dump(filter_config, FILTER_CONFIG_SAVE_PATH)

#################LOADING_QUESTIONS##################

from importlib import import_module

mod = import_module(HYPER_PARAMS['dataset_name'])
load_dataset = getattr(mod, "load_dataset")

question_packs = load_dataset(HYPER_PARAMS['eval_dataset_path'])

#################START_QA_PROCESS##################

for pack_name, questions, _ in question_packs:

    pack_tmp_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    if (HYPER_PARAMS['max_samples_per_pack'] < 0) or (HYPER_PARAMS['max_samples_per_pack'] > len(questions)):
        process = tqdm(range(len(questions)))
    else:
        process = tqdm(range(HYPER_PARAMS['max_samples_per_pack']))

    for i in process:
        process.set_postfix_str(pack_name)

        s_time = time()
        answer, info = qa_pipeline.answer(questions[i])
        e_time = time()

        answer_dump_file = f"{pack_tmp_dir}/answer_{i}"
        joblib.dump({'answer': answer, 'info': info, 'elapsed_time': e_time - s_time}, answer_dump_file)

# accumulate generate answers
elapsed_times = {}

for pack_name, _, _ in question_packs:

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
        accum_answers[answer_num] = answer_info['answer']
        elapsed_times[pack_name]['per_question'].append(answer_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['mean'] = np.mean(elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['median'] = np.median(elapsed_times[pack_name]['per_question'])

    answers_pack_path = f"{GENERATED_ANSWERS_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_answers, indent=1, ensure_ascii=False))

with open(QA_ELAPSED_TIME, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))
