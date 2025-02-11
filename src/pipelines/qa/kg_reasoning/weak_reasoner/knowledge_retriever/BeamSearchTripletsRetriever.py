from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set
import numpy as np
import heapq
from time import time
from collections import defaultdict
from collections import Counter
from copy import deepcopy, copy
from math import log

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig

from ......utils.data_structs import QueryInfo, Triplet, NodeType
from ......kg_model import KnowledgeGraphModel
from ......utils.data_structs import create_id
from ......utils import Logger
from ......db_drivers.vector_driver.embedders import EmbedderModelConfig
from ......db_drivers.vector_driver.utils import VectorDBInstance

@dataclass
class GraphBeamSearchConfig(BaseGraphSearchConfig):
    max_depth: int = 10
    num_paths: int = 50
    same_path_intersection_by_node: bool = True
    diff_paths_intersection_by_node: bool = True
    diff_paths_intersection_by_rel: bool = True
    mean_alpha: float = 0.75
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object , NodeType.hyper, NodeType.episodic])
    final_sorting_mode: str = 'finished_first' # 'finished_first' | 'mixed' | 'traversing_first'

class BeamSearchTripletsRetriever(AbstractTripletsRetriever):
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: GraphBeamSearchConfig = GraphBeamSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.config = search_config

    def calculate_path_score(self, path_len: int, accum_score: float) -> float:
        return accum_score / pow(path_len-1, self.config.mean_alpha)

    def calculate_triplet_score(self, raw_score: float) -> float:
        return -np.log(1 - raw_score)

    def get_available_nids(self, base_nid: str, prev_nid: str, cur_path_idx: int, traversing_paths) -> List[str]:
        adj_nids = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(base_nid, self.config.accepted_node_types)
        adj_nids = set(adj_nids).discard(prev_nid)

        if self.config.same_path_intersection_by_node:
            # Удаляем вершины, которые уже есть в текущем пути из числа смежных
            adj_nids.difference_update(traversing_paths[cur_path_idx][1])

        if self.config.diff_paths_intersection_by_node:
            # Удаляем вершины, которые есть в других путях из числа смежных для текущего пути
            for i in range(len(traversing_paths)):
                if i != cur_path_idx:
                    adj_nids.difference_update(traversing_paths[i][1])

        return adj_nids

    def get_available_rinfo(self, base_nid: str, adj_nids: List[str], cur_path_idx: int,
                            traversing_paths: List[List[List[Tuple[str,str,str]], Set[str], Set[str], float]]
                            ) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        shared_t_info = dict()
        rids_to_tids_map = defaultdict(list)
        for adj_nid in adj_nids:
            tmp_shared_ids = self.kg_model.graph_struct.db_conn.get_nodes_shared_ids(base_nid, adj_nid, type='both')
            tmp_ids_map = {item['t_id']: item['r_id'] for item in tmp_shared_ids}
            cur_tids = set(tmp_ids_map.keys())

            # Удаляем связи, которые уже есть в текущем пути
            tmp_shared_ids = cur_tids.discard(traversing_paths[cur_path_idx][2])

            if self.config.diff_paths_intersection_by_rel:
                # Удаляем связи, которые есть в других путях
                for i in range(len(traversing_paths)):
                    if i == cur_path_idx:
                        continue
                    other_path_unique_tids = traversing_paths[cur_path_idx][1]
                    tmp_shared_ids = cur_tids.discard(other_path_unique_tids)

            for t_id in cur_tids:
                shared_t_info[t_id] = adj_nid
                rids_to_tids_map[tmp_ids_map[t_id]].append(t_id)

        return shared_t_info, rids_to_tids_map

    def get_triplet_scores(self, query_vinstance: VectorDBInstance, shared_t_info: Dict[str, str],
                           rids_to_tids_map: Dict[str, List[str]]) -> List[Tuple[str, str, float]]:
        # в качества скора используется метрика расстояния [distance]
        # (её нужно вычесть из единицы, чтобы получить метрику близоси [similarity])
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

    def update_path_candidates(path_candidates: List[List[List[Tuple[str,str,str]], Set[str], Set[str], float]],
                               path_info: List[List[Tuple[str,str,str]], Set[str], Set[str], float],
                               triplet_scores: List[Tuple[str, str, float]]) -> None:
        # добавить новых кандидатов в пул
        for t_id, new_nid, t_score in triplet_scores:
            ext_path = deepcopy(path_info[0])
            ext_path.append((path_info[0][-1][2], t_id, new_nid))

            ext_unique_nids = copy(path_info[1])
            ext_unique_nids.add(new_nid)
            ext_unique_tids = copy(path_info[2])
            ext_unique_tids.add(t_id)

            new_accum_score = path_info[3] + t_score
            path_candidates.append([ext_path, ext_unique_nids, ext_unique_tids, new_accum_score])

    def filter_paths(self, ended_paths: List[Tuple[List[Tuple[str,str,str]], float]],
                     continuous_paths: List[Tuple[List[Tuple[str,str,str]], float]]) -> List[Tuple[List[Tuple[str,str,str]], float]]:
        # Готовим финальный список релевантных путей
        filtered_paths = []
        if self.config.final_sorting_mode == 'continuous_first':
            filtered_paths += sorted(continuous_paths, key=lambda tup:tup[1])[:self.config.num_paths]
            if len(filtered_paths) < self.config.num_paths:
                num_missed_paths = self.config.num_paths - len(filtered_paths)
                filtered_paths += sorted(ended_paths, key=lambda tup:tup[1])[:num_missed_paths]

        if self.config.final_sorting_mode == 'ended_first':
            filtered_paths += sorted(ended_paths, key=lambda tup:tup[1])[:self.config.num_paths]
            if len(filtered_paths) < self.config.num_paths:
                num_missed_paths = self.config.num_paths - len(filtered_paths)
                filtered_paths += sorted(continuous_paths, key=lambda tup:tup[1])[:num_missed_paths]

        elif self.config.final_sorting_mode == 'mixed':
            filtered_paths = sorted(continuous_paths + ended_paths, key=lambda tup:tup[1])[:self.config.num_paths]

        else:
            raise KeyError

        return filtered_paths

    def graph_beamsearch(self, query: str, node_id: str) -> List[Tuple[List[Tuple[str, str, str]], float]]:
        traversing_paths = [[[(None, None, node_id)], {node_id}, set(), 0.0]]
        ended_paths = []

        query_emb = self.kg_model.embeddings_struct.embedder.encode_queries([query])[0]
        query_vinstance = VectorDBInstance(embedding=query_emb)

        for _ in range(self.config.max_depth):
            path_candidates = list()

            if len(traversing_paths) < 1:
                # прекращаем построение путей, так как больше некуда двигаться
                break

            for i in range(len(traversing_paths)):
                path, _, _, accum_score = traversing_paths[i]
                prev_nid, tail_nid = path[-1][0], path[-1][2]

                adj_nids = self.get_available_nids(tail_nid, prev_nid, i, traversing_paths)
                if len(adj_nids) < 1:
                    # Если у tail-вершины нет смежных вершин, то считаем путь завершившимся
                    ended_paths.append([path, self.calculate_path_score(path, accum_score)])
                    continue

                shared_t_info, rids_to_tids_map = self.get_available_rinfo(tail_nid, adj_nids, i, traversing_paths)
                if len(shared_t_info) < 1:
                    # Если нет доступных связей для соединения tail-вершины с новой верщиной, то считаем путь завершившимся
                    ended_paths.append([path, self.calculate_path_score(path, accum_score)])
                    continue

                triplet_scores = self.get_triplet_scores(query_vinstance, shared_t_info, rids_to_tids_map)
                self.update_path_candidates(path_candidates, traversing_paths[i], triplet_scores)

            # Сортируем расширенный список путей по их релевантности и выбираем 'num_paths' лучших
            ordered_candidates = sorted(path_candidates, key=lambda tup:tup[3])
            traversing_paths = ordered_candidates[:self.config.num_paths]

        continuous_paths = []
        for path_info in traversing_paths:
            continuous_paths.append([path_info[0], self.calculate_path_score(len(path_info[0]), path_info[3])])
        filtered_paths = self.filter_paths(ended_paths, continuous_paths)

        return filtered_paths

    def search(self, query: str, node_id: str) -> List[Triplet]:
        paths_info = self.graph_beamsearch(query, node_id)

        uniques_tids = set()
        for path, _ in paths_info:
            for triplet_info in path[1:]:
                uniques_tids.add(triplet_info[1])

        extracted_triplets = self.kg_model.graph_struct.db_conn.read(list(uniques_tids))
        return extracted_triplets

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
