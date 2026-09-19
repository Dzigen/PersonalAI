print("Scoring generated answers with RAGAS")

import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
import torch
import joblib
from time import time
import asyncio
from collections import Counter
from tqdm import tqdm
from typing import Dict, List
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

RAGAS_SOURCE_PATH = f"{WORKSPACE_CONTAINER_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EVAL_PARAMS['ragas_path']}/.."
sys.path.insert(0, RAGAS_SOURCE_PATH)

from my_ragas.RagasMetrics import RagasMetricsConfig, RagasMetrics
from src.agents import AgentDriverConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.utils.data_structs import TripletCreator, SearchPlanInfo
from src.utils import ModuleType, CompositeModuleResult

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

QA_TRACES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['qa_traces_name']}"

TMP_RAGAS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_ragas_name']}"
RAGAS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['ragas_name']}"

EXP_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EVALUATE_DIR = f"{EXP_DIR}/{EVAL_PARAMS['ragas_kv_dir']}"

SETTINGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
EVAL_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['eval']}"

####################################################
print("3. Setting Caching mechanism")

ragas_raw_config = EVAL_PARAMS['ragas_llm_config']

if ragas_raw_config['caching']:
    kvdriver_config = KeyValueDriverConfig(
        db_vendor='inmemory_kv',
        db_config=KVDBConnectionConfig(
            need_to_clear=ragas_raw_config['cache_need_to_clear'],
            db_info=ragas_raw_config['cache_db_info'],
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
print("4. Setting Ragas")

adriver_config = AgentDriverConfig(**ragas_raw_config['agent_driver_config'])
adriver_config.formate_fields()

ragas_config = RagasMetricsConfig(
    adriver_config=adriver_config
)

ragas_evaluator = RagasMetrics(ragas_config, kvdriver_config)

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
print("5. Start scoring answers with Ragas")

answers_pack_names = os.listdir(GENERATED_ANSWERS_DIR)
for pack_name in answers_pack_names:
    answers_info = load_json(f"{GENERATED_ANSWERS_DIR}/{pack_name}")

    pack_tmp_dir = f"{TMP_RAGAS_DIR}/{pack_name.split('.')[0]}"
    if not os.path.exists(pack_tmp_dir):
        os.mkdir(pack_tmp_dir)

    process = tqdm(answers_info.items())
    for a_idx, a_info in process:
        process.set_postfix_str(f"pack: {pack_name}; idx: {a_idx}, is_genanswer_none - {a_info['gen_answer'] is None}")

        if a_info['gen_answer'] is None:
            continue

        trace_info: CompositeModuleResult = joblib.load(f"{QA_TRACES_DIR}/{pack_name.split('.')[0]}/trace_{a_idx}")

        retrieved_contexts: List[str] = []
        contexts_source: str = None

        #  Извлекаем контексты из трейса QA-пайплайна
        postprocess_query_trace = trace_info.detailed_result.modules_categories[ModuleType.stage]['postprocess_answer'][0]
        subqueries = postprocess_query_trace.summary.context['positional_arguments'][1].sub_queries
        if len(subqueries) > 1:
            subanswers = postprocess_query_trace.summary.context['positional_arguments'][1].sub_answers
            for subquery, subanswer in zip(subqueries, subanswers):
                retrieved_contexts.append(f"{subquery} - {subanswer}")
            contexts_source = 'subqueries_summ'
        else:
            contexts_source = "kg_reasoner"
            process_query_trace = trace_info.detailed_result.modules_categories[ModuleType.stage]['process_query'][0]
            kg_reasoner_trace = process_query_trace.detailed_result.modules_categories[ModuleType.stage]['perform'][0]

            answer_generation_input_trace = kg_reasoner_trace.detailed_result.get_results_sequence()[-1][-1].context['positional_arguments'][-1]
            if type(answer_generation_input_trace) is SearchPlanInfo:
                for step_query, step_answer in zip(answer_generation_input_trace.search_steps, answer_generation_input_trace.steps_answers):
                    retrieved_contexts.append(f"{step_query} - {step_answer}")

            elif type(answer_generation_input_trace) is list:
                for triplet in answer_generation_input_trace:
                    retrieved_contexts.append(TripletCreator.stringify(triplet)[1])
            else:
                raise TypeError(f"answer_generation_input_trace: {answer_generation_input_trace}")
        #

        scores = dict()

        s_time = time()
        eval_suite = {
            'user_input':a_info['question'], 'reference': a_info['gold_answer'],
            'response': a_info['gen_answer'], 'retrieved_contexts': retrieved_contexts
        }
        ragas_metrics = ['context_relevance', 'faithfulness', 'response_groundedness']
        for metric_name in ragas_metrics:
            cache_hit, output = ragas_evaluator.get_cached_score(metric_name, **eval_suite)
            if cache_hit:
                scores[metric_name] = output
            else:
                scores[metric_name] = asyncio.run(ragas_evaluator.perform(metric_name, **eval_suite))
                ragas_evaluator.cache_score(metric_name, scores[metric_name], **eval_suite)

        e_time = time()

        ragas_dump_file = f"{pack_tmp_dir}/ragas_{a_idx}"
        ragas_result = {
            'contexts_source': contexts_source, 'ragas_scores': scores,
            'info': None, 'elapsed_time': e_time - s_time
        }
        #print(ragas_result)
        joblib.dump(ragas_result, ragas_dump_file)

####################################################
print("6. Accumulating RAGAS scores")

ragas_pack_names = os.listdir(TMP_RAGAS_DIR)
for pack_name in ragas_pack_names:
    print(pack_name)

    pack_tmp_dir = f"{TMP_RAGAS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_score_dumps = os.listdir(pack_tmp_dir)
    accum_score = {
        'ragas': {
            'response_groundedness': dict(), 'context_relevance': dict(),
            'faithfulness': dict(),
        },
        'contexts_source': dict(),
        'elapsed_time': dict(),
        'answer_score_map': dict(),
        'answer_time_map': dict()
    }

    contexts_sources: List[str] = []
    for tmp_dump in tqdm(tmp_score_dumps):
        answer_info = joblib.load(f"{pack_tmp_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])

        accum_score['answer_time_map'][answer_num] = answer_info['elapsed_time']
        accum_score['answer_score_map'][answer_num] = answer_info['ragas_scores']

        contexts_sources.append(answer_info['contexts_source'])

    accum_score['elapsed_time']['sum'] = sum(
        list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['mean'] = np.mean(
        list(accum_score['answer_time_map'].values()))
    accum_score['elapsed_time']['median'] = np.median(
        list(accum_score['answer_time_map'].values()))

    for ragas_metric_name in ragas_metrics:
        spec_scores = list(map(lambda scores: scores[ragas_metric_name], accum_score['answer_score_map'].values()))
        filtered_scores = list(filter(lambda score: (score is not None) and (not np.isnan(score)), spec_scores))
        accum_score['ragas'][ragas_metric_name]['mean'] = np.mean(filtered_scores) if len(filtered_scores) > 0 else 0.0
        accum_score['ragas'][ragas_metric_name]['median'] = np.median(filtered_scores) if len(filtered_scores) > 0 else 0.0

    accum_score['contexts_source'] = dict(Counter(contexts_sources))

    save_json(accum_score, f"{RAGAS_DIR}/{pack_name}.json")

####################################################
print("7. Saving eval params")

with open(EVAL_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EVAL_PARAMS, fd, default_flow_style=False, sort_keys=False)

ragas_evaluator.cachekv.kv_conn.close_connection()

print("############ DONE ############")
