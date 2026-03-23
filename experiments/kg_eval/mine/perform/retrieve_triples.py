print("Start Memory-model inferencing...")
import sys
import yaml
import joblib
from typing import List, Tuple, Dict, Set, Union
from pprint import pprint
import os
import numpy as np
from datasets import load_from_disk
import pandas as pd
from collections import Counter
from time import time
import datetime
from tqdm import tqdm
import json

import sys
BASE_PATH = '/home/workspace' # TO CHANGE
sys.path.insert(0, BASE_PATH)

from src.utils import Triplet, TripletCreator, NodeType
from src.rerankers import RerankerDriverConfig, RerankerDriver
from src.rerankers.methods import EnsembleFusionRerankerConfig
from src.utils.data_structs import NodeType, NodeInfo, NODES_TYPES_MAP

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

CONTAINER_ENV_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg_env_path']}"
SPEC_ENV_PATH = f"{CONTAINER_ENV_PATH}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig

####################################################
print("2. Setting paths")

# EXP PATHS
EXPS_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXP_RESULTS_DIR = f"{EXPS_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

DATASET_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{SPECEXP_PARAMS['DATASET_NAME']}"

TMP_RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_retrieved_triples_name']}"
RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['retrieved_triples_name']}"

ELAPSED_TIME_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"

# KG PATHS
DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPECEXP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"

####################################################
print("3. Loading configs")

kgmodel_config: KnowledgeGraphModelConfig = joblib.load(KG_MODEL_CONFIG_PATH)

print("KG MODEL_CONFIG:")
pprint(kgmodel_config)
####################################################
print("4. Setting KG Model")

kg_model = KnowledgeGraphModel(kgmodel_config)
print("kg_model:")
pprint(kg_model.count_items(detailed=True))


NODES_RERANKDRIVER_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['dense_nodes', 'bm25_nodes'],
        weights=[0.4, 0.6]
    )
)
nodes_retriever = RerankerDriver.specify(
    NODES_RERANKDRIVER_CONFIG,
    kg_model.graph_embeddings.nodes_vcomposers[NodeType.object])

TRIPLES_RERANKDRIVER_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['dense_triplets', 'bm25_triplets'],
        weights=[0.9, 0.1]
    )
)
triples_retriever = RerankerDriver.specify(
    TRIPLES_RERANKDRIVER_CONFIG,
    kg_model.graph_embeddings.triplets_vcomposer)

FORMATED_ACCEPTED_N_TYPES = [NODES_TYPES_MAP[raw_n_type] for raw_n_type in SPECEXP_PARAMS['RETRIEVE_SETTING']['accepted_nodes_types']]

####################################################
print("6. Loading MINE-dataset")

def mine_load(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    original_dataset = load_from_disk(f"{dataset_path}/original") # 101
    packs = []
    for i in range(len(original_dataset)):
        pack_name = original_dataset['id'][i]
        queries = original_dataset['generated_queries'][i]
        if len(queries) < 1:
            continue
        else:
            packs.append((pack_name, queries))
    print(f"packs: {len(packs)}")
    return packs

queries_packs = mine_load(DATASET_PATH)

####################################################
print("7. Start inferencing")

def explore_neighbors(kg_model: KnowledgeGraphModel, query: str, current_node: NodeInfo,
                      prev_node: Union[None, NodeInfo], current_depth: int, max_depth: int = 2) -> Set[str]:
    retrieved_triple_rids: Set[str] = set()
    rid_to_nnid_map: Dict[str, str] = dict()

    print(f"NODE NEIGHBORS EXPLORE: current_node - {current_node}; prev_node - {prev_node}; current_depth - {current_depth}; max_depth - {max_depth}")

    if current_depth > max_depth:
        print("MAX DEPTH REACHED!")
        return

    # Получаем идентификаторы триплетов, инцедентных current_node-вершине
    adjacent_nodes: List[NodeInfo] = kg_model.graph_struct.db_conn.get_adjacent_nodes(
        current_node, FORMATED_ACCEPTED_N_TYPES)
    incident_triple_rids: Set[str] = set()
    for neighbor in adjacent_nodes:
        if (prev_node is not None) and (neighbor.to_str() == prev_node.to_str()):
            continue

        raw_output = kg_model.graph_struct.db_conn.get_nodes_shared_ids(
            current_node, neighbor, id_type='relation')
        shared_rids = list(map(lambda item: item['r_id'], raw_output))
        rid_to_nnid_map.update({r_id: neighbor for r_id in shared_rids})

        incident_triple_rids.update(shared_rids)

    #print(f"BASE INCIDENT TRIPLES AMOUNT FOR NODE {current_node}: {len(incident_triple_rids)}")

    # Отбираем max_triples_per_node-триплетов, инцидентных current_node-вершине и релевантных для query
    # по оценке близости из векторных представлений
    if SPECEXP_PARAMS['RETRIEVE_SETTING']['max_triples_per_node'] != -1:
        filtered_triples = triples_retriever.run(
            query, top_k=SPECEXP_PARAMS['RETRIEVE_SETTING']['max_triples_per_node'],
            subset_ids=list(incident_triple_rids))
        retrieved_triple_rids.update(set(map(lambda item: item.id, filtered_triples)))
    else:
        retrieved_triple_rids.update(incident_triple_rids)

    print(f"FILTERED INCIDENT TRIPLES FOR NODE {current_node}: {len(retrieved_triple_rids)} {retrieved_triple_rids}")

    # Отбираем max_nodes_per_depth-вершин, смежных с current_node-вершиной и релевантных для query
    # по оценке близости из векторных представлений
    max_nodes_per_depth = SPECEXP_PARAMS['RETRIEVE_SETTING']['max_nodes_per_depth']
    if max_nodes_per_depth == -1:
        max_nodes_per_depth = len(incident_triple_rids)

    filtered_triples = triples_retriever.run(
            query, top_k=max_nodes_per_depth,
            subset_ids=list(incident_triple_rids))
    filtered_triple_rids = list(map(lambda item: item.id, filtered_triples))
    topk_neighbor_nodes = [rid_to_nnid_map[rid] for rid in filtered_triple_rids]

    print(f"FILTERED NEIGHBOUR NODES FOR NODE {current_node}: {len(topk_neighbor_nodes)} {topk_neighbor_nodes}")

    # Запускаем обход/отбор триплетов по отобранным вершинам
    for neighbor in topk_neighbor_nodes:
        new_triple_rids = explore_neighbors(
            kg_model, query, neighbor, current_node, current_depth + 1, max_depth)
        if new_triple_rids is not None:
            retrieved_triple_rids.update(new_triple_rids)

    print(f"RETURNING FROM DEPTH={current_depth} TO DEPTH={current_depth-1}")
    print(f"RETRIEVED TRIPLES IN TOTAL: {len(retrieved_triple_rids)}")

    return retrieved_triple_rids

print(f"start time: {datetime.datetime.now()}")
QUERIES_COUNTER = 0
for pack_name, queries in tqdm(queries_packs):

    if len(queries) < 1:
        print(f"Empty queries set; pack: {pack_name}")
        continue

    pack_tmp_triples_dir = f"{TMP_RETRIEVED_TRIPLES_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_triples_dir):
        os.mkdir(pack_tmp_triples_dir)

    for i in range(len(queries)):
        QUERIES_COUNTER += 1
        s_time = time()

        matched_objects = list(map(
            lambda node: NodeInfo(id=node.id, text=node.document, type=NodeType.object),
            nodes_retriever.run(queries[i], top_k=SPECEXP_PARAMS['RETRIEVE_SETTING']['max_matched_nodes'], includes=['documents'])
        ))

        print(f"==== QUERY #{pack_name}.{i}: {queries[i]}")
        print(f"MATCHED OBJECT NODES: {len(matched_objects)} {matched_objects}")

        print("== START GRAPH EXPLORATION ==")
        retrieved_triple_rids: Set[str] = set()
        for object_node in matched_objects:
            retrieved_triple_rids.update(
                explore_neighbors(
                    kg_model, queries[i], object_node, None, 1,
                    SPECEXP_PARAMS['RETRIEVE_SETTING']['max_explore_depth']
                )
            )
        print("== END GRAPH EXPLORATION ==")

        max_triples_in_total = SPECEXP_PARAMS['RETRIEVE_SETTING']['max_triples_in_total']
        if max_triples_in_total == -1:
            max_triples_in_total = len(retrieved_triple_rids)

        filtered_triples = triples_retriever.run(
            queries[i], top_k=max_triples_in_total,
            subset_ids=list(retrieved_triple_rids))
        retrieved_triples = list(map(lambda item: item.document, filtered_triples))

        formated_retrieved_triples = '\n'.join(retrieved_triples)
        print(f"RETRIEVED TRIPLES IN TOTAL (AFTER FILTERING): {len(retrieved_triples)}\n{formated_retrieved_triples}")

        e_time = time()

        triples_dump_file = f"{pack_tmp_triples_dir}/triples_{i}"
        joblib.dump({'retrieved_triples': retrieved_triples, 'elapsed_time': e_time - s_time}, triples_dump_file)
print(f"endtime time: {datetime.datetime.now()}")

print(f"USED QUERIES IN TOTAL: {QUERIES_COUNTER}")

####################################################
print("8. Accumulating retrieved triples")

elapsed_times: Dict[str,Dict[str, float]] = dict()
for pack_name, queries in queries_packs:
    print(pack_name)

    pack_tmp_triples_dir = f"{TMP_RETRIEVED_TRIPLES_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_triples_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_triples_dumps = os.listdir(pack_tmp_triples_dir)

    accum_triples: Dict[str,Dict[str, str]] = dict()
    elapsed_times[pack_name] = {'per_query': []}
    for tmp_dump in tqdm(tmp_triples_dumps):
        triples_info = joblib.load(f"{pack_tmp_triples_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])

        retrieved_triples: List[str] = triples_info['retrieved_triples']

        accum_triples[answer_num] = {
            'query': queries[answer_num],
            'retrieved_triples': retrieved_triples
        }

        elapsed_times[pack_name]['per_query'].append(triples_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(
        elapsed_times[pack_name]['per_query'])
    elapsed_times[pack_name]['mean'] = np.mean(
        elapsed_times[pack_name]['per_query'])
    elapsed_times[pack_name]['median'] = np.median(
        elapsed_times[pack_name]['per_query'])

    answers_pack_path = f"{RETRIEVED_TRIPLES_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_triples, indent=1, ensure_ascii=False))

with open(ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))

print("############ DONE ############")

kg_model.close_connections()
