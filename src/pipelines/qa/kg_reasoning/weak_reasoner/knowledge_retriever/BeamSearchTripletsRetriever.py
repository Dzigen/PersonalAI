####
# Author:   Mikhail Menschikov
# Email:    menshikov.mikhail.2001@gmail.com
# Created:  11.02.2025
# (c) Copyright by Skoltech AI Center.
####

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Union
from collections import defaultdict
from collections import Counter
from copy import deepcopy, copy
import numpy as np

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig

from ......utils.data_structs import QueryInfo, Triplet, NodeType
from ......kg_model import KnowledgeGraphModel
from ......utils.data_structs import create_id, NODES_TYPES_MAP
from ......utils import Logger
from ......db_drivers.vector_driver.utils import VectorDBInstance
from ......utils.cache_kv import CacheKV, CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig

@dataclass
class TraversingPath:
    path: List[Tuple[str,str,str]]
    unique_nids: Set[str]
    unique_tids: Set[str]
    accum_score: float

@dataclass
class TraversedPath:
    path: List[Tuple[str,str,str]]
    score: float

@dataclass
class GraphBeamSearchConfig(BaseGraphSearchConfig):
    # Максимальная глубина построенных путей
    max_depth: int = 10
    # Максимальное количество построенных путей
    max_paths: int = 50
    # Если True, то пути могут пересекаться сами с собой по вершинам, иначе False
    same_path_intersection_by_node: bool = True
    # Если True, то разные пути могут пересекаться по вершинам, иначе False
    diff_paths_intersection_by_node: bool = True
    # Если True, то разные пути могут пересекаться по связям, иначе False
    diff_paths_intersection_by_rel: bool = True
    # Гиперпараметр, отвечающий за учёт длины построенного пути при усреднении его ценности (релевантности).
    # См. calculate_triplet_score- и calculate_path_score-методы.
    mean_alpha: float = 0.75
    # Типы вершины, которые можно обходить во время построения путей
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object , NodeType.hyper, NodeType.episodic])
    # Способ финальной фильтрации полученного набора путей. В результате поиска будет сформировано два набора путей:
    # (1) ended - пути, которые завершились до достижения заданного ограничения на глубину и (2) continious - пути,
    # которые достигли заданного ограничения на глубину. У каждого такого пути есть оценка его суммарной релевантности.
    # Если будет указано 'ended_first'-значение, то: ended-пути будут отсортированы по убыванию релевантности и выбраны
    # первые 'max_paths'-путей. Если ended-путей меньше чем 'max_paths'-значения, то continious-пути будут отсортированы
    # по релевантности и из них будут выбраны первые N недостающих путей. Если будет указано 'continuous_first'-значение,
    # то пути будут выбираться по аналогии с 'ended_first'-значением, только сначала сортировка/выбор по continuous-путям,
    # а потом по ended-путям. Если будет указано 'mixed'-значение, то ended- и continuous-пути будут объединены в один список,
    # отсортированы по убыванию релевантности и из полученного списко будет выбрано первых 'max_paths'-путей.
    final_sorting_mode: str = 'mixed' # 'ended_first' | 'mixed' | 'continuous_first'
    cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None


class BeamSearchTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger,
                 search_config: Union[GraphBeamSearchConfig, Dict] = GraphBeamSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model

        if type(search_config) is Dict:
            if 'accepted_node_types' in search_config:
                search_config['accepted_node_types'] = list(map(lambda k: NODES_TYPES_MAP[k], search_config['accepted_node_types']))

            if 'cache_kvdriver_config' in search_config:
                search_config['cache_kvdriver_config'] = KeyValueDriverConfig(**search_config['cache_kvdriver_config'])
                search_config['cache_kvdriver_config'].db_config = KVDBConnectionConfig(**search_config['cache_kvdriver_config'].db_config)

            search_config = GraphBeamSearchConfig(**search_config)
        self.config = search_config

        if self.config.cache_kvdriver_config is not None:
            self.cachekv = CacheKV(self.config.cache_kvdriver_config)
        else:
            self.cachekv = None

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        return [self.config, self.kg_model.embeddings_struct.config,
                self.kg_model.graph_struct.config, query_info]

    def calculate_path_score(self, path_len: int, accum_score: float) -> float:
        return accum_score / pow(path_len-1, self.config.mean_alpha)

    def calculate_triplet_score(self, raw_score: float) -> float:
        # Note: в качества скора используется метрика косинусного расстояния [distance]
        # (её нужно вычесть из единицы, чтобы получить метрику косинусной близоси [similarity])
        return -np.log(1 - raw_score)

    def get_available_nids(self, base_nid: str, cur_path_idx: int,
            traversing_paths: List[TraversingPath], prev_nid: str = None) -> List[str]:
        adj_nids = self.kg_model.graph_struct.db_conn.get_adjecent_nids(base_nid, self.config.accepted_node_types)
        if prev_nid is not None:
            adj_nids = set(adj_nids).discard(prev_nid)

        if not self.config.same_path_intersection_by_node:
            # Удаляем вершины, которые уже есть в текущем пути из числа смежных
            adj_nids.difference_update(traversing_paths[cur_path_idx].unique_nids)

        if not self.config.diff_paths_intersection_by_node:
            # Удаляем вершины, которые есть в других путях из числа смежных для текущего пути
            for i in range(len(traversing_paths)):
                if i != cur_path_idx:
                    adj_nids.difference_update(traversing_paths[i].unique_nids)

        return adj_nids

    def get_available_rinfo(
            self, base_nid: str, adj_nids: List[str], cur_path_idx: int,
            traversing_paths: List[TraversingPath]) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        shared_t_info = dict()
        rids_to_tids_map = defaultdict(list)
        for adj_nid in adj_nids:
            tmp_shared_ids = self.kg_model.graph_struct.db_conn.get_nodes_shared_ids(base_nid, adj_nid, type='both')
            tmp_ids_map = {item['t_id']: item['r_id'] for item in tmp_shared_ids}
            cur_tids = set(tmp_ids_map.keys())

            # Удаляем связи, которые уже есть в текущем пути
            tmp_shared_ids = cur_tids.difference(traversing_paths[cur_path_idx].unique_tids)

            if not self.config.diff_paths_intersection_by_rel:
                # Удаляем связи, которые уже есть в других путях
                for i in range(len(traversing_paths)):
                    if i != cur_path_idx:
                        tmp_shared_ids.difference_update(traversing_paths[i].unique_tids)

            for t_id in list(tmp_shared_ids):
                shared_t_info[t_id] = adj_nid
                rids_to_tids_map[tmp_ids_map[t_id]].append(t_id)

        return shared_t_info, rids_to_tids_map

    def get_triplet_scores(self, query_vinstance: VectorDBInstance, shared_t_info: Dict[str, str],
                           rids_to_tids_map: Dict[str, List[str]]) -> List[Tuple[str, str, float]]:
        r_ids = list(rids_to_tids_map.keys())
        scored_rels = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
            [query_vinstance], n_results=len(r_ids), includes=[], where={"id": {"$in": r_ids}})[0]

        formated_scores_info = []
        for raw_score, triplet_info in scored_rels:
            formated_scores_info.append(
                (triplet_info.id, self.calculate_triplet_score(raw_score)))

        extended_scores_info = []
        for r_id, t_score in formated_scores_info:
            for t_id in rids_to_tids_map[r_id]:
                extended_scores_info.append((t_id, shared_t_info[t_id], t_score))

        return extended_scores_info

    def update_path_candidates(path_candidates: List[TraversingPath], pinfo: TraversingPath,
                               triplet_scores: List[Tuple[str, str, float]]) -> None:
        # добавить новых кандидатов (дополненных вариантов i-ого пути) в пул
        for t_id, new_nid, t_score in triplet_scores:
            ext_trpath = deepcopy(pinfo)

            ext_trpath.path.append((ext_trpath.path[-1][2], t_id, new_nid))
            ext_trpath.unique_nids.add(new_nid)
            ext_trpath.unique_tids.add(t_id)
            ext_trpath.accum_score += t_score

            path_candidates.append(ext_trpath)

    def filter_paths(self, ended_paths: List[TraversedPath],
                     continuous_paths: List[TraversedPath]) -> List[TraversedPath]:
        # Готовим финальный список релевантных путей
        filtered_paths = []
        if self.config.final_sorting_mode == 'continuous_first':
            filtered_paths += sorted(continuous_paths, key=lambda pinfo:pinfo.score)[:self.config.max_paths]
            if len(filtered_paths) < self.config.max_paths:
                num_missed_paths = self.config.max_paths - len(filtered_paths)
                filtered_paths += sorted(ended_paths, key=lambda pinfo:pinfo.score)[:num_missed_paths]

        if self.config.final_sorting_mode == 'ended_first':
            filtered_paths += sorted(ended_paths, key=lambda pinfo: pinfo.score)[:self.config.max_paths]
            if len(filtered_paths) < self.config.max_paths:
                num_missed_paths = self.config.max_paths - len(filtered_paths)
                filtered_paths += sorted(continuous_paths, key=lambda pinfo:pinfo.score)[:num_missed_paths]

        elif self.config.final_sorting_mode == 'mixed':
            filtered_paths = sorted(continuous_paths + ended_paths, key=lambda pinfo:pinfo.score)[:self.config.max_paths]

        else:
            raise KeyError

        return filtered_paths

    def graph_beamsearch(self, query: str, node_id: str) -> List[TraversedPath]:
        traversing_paths = [TraversingPath(
            path=[(None, None, node_id)], unique_nids={node_id},
            unique_tids=set(), accum_score=0.0)]
        ended_paths = []

        query_emb = self.kg_model.embeddings_struct.embedder.encode_queries([query])[0]
        query_vinstance = VectorDBInstance(embedding=query_emb)

        for _ in range(self.config.max_depth):
            path_candidates = list()

            if len(traversing_paths) < 1:
                # прекращаем построение путей, так как больше некуда двигаться
                break

            for i in range(len(traversing_paths)):
                cur_path_info = traversing_paths[i]
                prev_nid, tail_nid = cur_path_info.path[-1][0], cur_path_info.path[-1][2]

                adj_nids = self.get_available_nids(tail_nid, i, traversing_paths, prev_nid=prev_nid)
                if len(adj_nids) < 1:
                    # Если у tail-вершины нет смежных вершин, то считаем путь завершившимся
                    ended_paths.append([deepcopy(cur_path_info.path), self.calculate_path_score(
                        len(cur_path_info.path), cur_path_info.accum_score)])
                    continue

                shared_t_info, rids_to_tids_map = self.get_available_rinfo(tail_nid, adj_nids, i, traversing_paths)
                if len(shared_t_info) < 1:
                    # Если нет доступных связей для соединения tail-вершины с новой вершиной,
                    # то считаем путь завершившимся.
                    ended_paths.append([deepcopy(cur_path_info.path), self.calculate_path_score(
                        len(cur_path_info.path), cur_path_info.accum_score)])
                    continue

                triplet_scores = self.get_triplet_scores(query_vinstance, shared_t_info, rids_to_tids_map)
                self.update_path_candidates(path_candidates, traversing_paths[i], triplet_scores)

            # Сортируем (по возрастанию) расширенный список путей
            # по их релевантности и выбираем 'max_paths' лучших
            ordered_candidates = sorted(path_candidates, key=lambda pinfo: pinfo.accum_score)
            traversing_paths = ordered_candidates[:self.config.max_paths]

        continuous_paths = []
        for path_info in traversing_paths:
            continuous_paths.append(
                TraversedPath(path=path_info.path, score=self.calculate_path_score(
                    len(path_info.path), path_info.accum_score)))
        filtered_paths = self.filter_paths(ended_paths, continuous_paths)

        return filtered_paths

    def search(self, query: str, node_id: str) -> List[Triplet]:
        paths_info = self.graph_beamsearch(query, node_id)

        uniques_tids = set()
        for p_info in paths_info:
            # Note: в нулевом кортеже у всех путей
            # только в координате для хранения id конечной вершины
            # не лежит None.
            for triplet_info in p_info.path[1:]:
                uniques_tids.add(triplet_info[1])

        extracted_triplets = self.kg_model.graph_struct.db_conn.read(list(uniques_tids))
        return extracted_triplets

    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        node_ids = set([node.id for node in query_info.linked_nodes])
        self.log(f"Вершины, для которых будет запущейн BeamSearch: {node_ids}", verbose=self.verbose)

        unique_triplets = dict()
        for node_id in node_ids:
            self.log(f"Запускаем BeamSearch по вершине с id: {node_id}", verbose=self.verbose)
            tmp_triplets = self.search(query_info.query, node_id)
            self.log(f"Количество извлечённых триплетов для данной вершины: {len(tmp_triplets)}", verbose=self.verbose)
            unique_triplets.update({triplet.relation.id: triplet for triplet in tmp_triplets})

        self.log(f"Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: {len(unique_triplets)}", verbose=self.verbose)
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in unique_triplets.values()])}", verbose=self.verbose)

        return list(unique_triplets.values())
