####
# Author:   Mikhail Menschikov
# Email:    menshikov.mikhail.2001@gmail.com
# Created:  11.02.2025
####

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Union
from collections import defaultdict
from collections import Counter
from time import time
from copy import deepcopy
import numpy as np

from .configs import BSGS_RERANKDRIVER_DEFAULT_CONFIG
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, NodeType, NodeInfo, from_str_to_nodeinfo
from .......kg_model import KnowledgeGraphModel
from .......utils.data_structs import create_id, NODES_TYPES_MAP
from .......utils import Logger, accumulate_step_info, ReturnInfo
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig
from .......rerankers import RerankerDriver, RerankerDriverConfig
from .......rerankers.methods import SingleStepReranker


@dataclass
class TraversingPath:
    path: List[Tuple[NodeInfo, str, NodeInfo]]
    unique_ntypedids: Set[str]
    unique_tids: Set[str]
    accum_score: float


@dataclass
class TraversedPath:
    path: List[Tuple[NodeInfo, str, NodeInfo]]
    score: float


@dataclass
class GraphBeamSearchConfig(BaseGraphSearchConfig):
    """Конфигурация BeamSearchTripletsRetriever-алгоритма обхода графа.

    :param reranker_driver_config: Конфигурация Retrieve/Rerank-оператора. Значение по умолчанию BSGS_RERANKDRIVER_DEFAULT_CONFIG.
    :type reranker_driver_config: Union[Dict,RerankerDriverConfig], optional
    :param vdbname_for_scores: ... . Значение по умолчанию 'dense_triplets'.
    :type vdbname_for_scores: str, optional
    :param max_depth: Максимальная глубина построенных/пройденных путей. Значение по умолчанию 10.
    :type max_depth: int, optional
    :param max_paths: Максимальное количество построенных/пройденных путей. Значение по умолчанию 50.
    :type max_paths: int, optional
    :param same_path_intersection_by_node: Если True, то пути могут пересекаться сами с собой по вершинам, иначе False. Значение по умолчанию False.
    :type same_path_intersection_by_node: bool, optional
    :param diff_paths_intersection_by_node: Если True, то разные пути могут пересекаться по вершинам, иначе False. Значение по умолчанию False.
    :type diff_paths_intersection_by_node: bool, optional
    :param diff_paths_intersection_by_rel: Если True, то разные пути могут пересекаться по связям, иначе False. Значение по умолчанию False.
    :type diff_paths_intersection_by_rel: bool, optional
    :param mean_alpha: Гиперпараметр, отвечающий за учёт длины построенного пути при усреднении его ценности (релевантности). См. calculate_triplet_score- и calculate_path_score-методы. Значение по умолчанию 0.75.
    :type mean_alpha: float, optional
    :param accepted_node_types: Типы вершины, которые можно обходить во время построения путей. Значение по умолчанию [NodeType.object , NodeType.hyper, NodeType.episodic].
    :type accepted_node_types: List[NodeType], optional
    :param final_sorting_mode: Способ финальной фильтрации полученного набора путей. В результате поиска будет сформировано два набора путей: (1) ended - пути, которые завершились до достижения заданного ограничения на глубину и (2) continious - пути, которые достигли заданного ограничения на глубину. У каждого такого пути есть оценка его суммарной релевантности. Если будет указано 'ended_first'-значение, то: ended-пути будут отсортированы по убыванию релевантности и выбраны первые 'max_paths'-путей. Если ended-путей меньше чем 'max_paths'-значения, то continious-пути будут отсортированы по релевантности и из них будут выбраны первые N недостающих путей. Если будет указано 'continuous_first'-значение, то пути будут выбираться по аналогии с 'ended_first'-значением, только сначала сортировка/выбор по continuous-путям, а потом по ended-путям. Если будет указано 'mixed'-значение, то ended- и continuous-пути будут объединены в один список, отсортированы по убыванию релевантности и из полученного списко будет выбрано первых 'max_paths'-путей. Значение по умолчанию 'mixed'.
    :type final_sorting_mode: str, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveBFSTripletsRetriever-класса. Значение по умолчанию 'qa_beamsearch_t_retriever_cache'.
    :type cache_table_name: str, optional
    """
    reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(default_factory=lambda: BSGS_RERANKDRIVER_DEFAULT_CONFIG)
    vdbname_for_scores: str = 'dense_triplets'
    max_depth: int = 3
    max_paths: int = 18
    same_path_intersection_by_node: bool = False
    diff_paths_intersection_by_node: bool = False
    diff_paths_intersection_by_rel: bool = False
    mean_alpha: float = 0.75
    accepted_node_types: List[NodeType] = field(
        default_factory=lambda: [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    final_sorting_mode: str = 'mixed'  # 'ended_first' | 'mixed' | 'continuous_first'

    cache_table_name: str = 'qa_beamsearch_t_retriever_cache'

    def to_str(self):
        str_reranker = f"{self.vdbname_for_scores};{self.reranker_driver_config.to_str()}"
        str_accepted_nodes = ";".join(sorted(list(map(lambda v: v.value, self.accepted_node_types))))
        str_values = f"{self.max_depth};{self.max_paths};{self.mean_alpha};{str_accepted_nodes};{self.final_sorting_mode}"
        str_bools = f"{self.same_path_intersection_by_node};{self.diff_paths_intersection_by_node};{self.diff_paths_intersection_by_rel}"

        return f"{str_values};{str_bools};{str_reranker}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = GraphBeamSearchConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, node_type in enumerate(self.accepted_node_types):
            if not isinstance(node_type, NodeType):
                self.accepted_node_types[i] = NODES_TYPES_MAP[node_type]

        if isinstance(self.reranker_driver_config, dict):
            self.reranker_driver_config = RerankerDriverConfig.from_dict(self.reranker_driver_config)
        else:
            self.reranker_driver_config.formate_fields()


class BeamSearchTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе BeamSeach-алгоритма обхода.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param search_config: Конфигурация BeamSearchTripletsRetriever-алгоритма. Значение по умолчанию GraphBeamSearchConfig().
    :type search_config: Union[GraphBeamSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger,
                 search_config: Union[GraphBeamSearchConfig, Dict] = GraphBeamSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, verbose: bool = False) -> None:
        if isinstance(search_config, dict):
            search_config = GraphBeamSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: GraphBeamSearchConfig = search_config

        self.kg_model = kg_model

        self.scorer = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.triplets_vcomposer
        )
        if not isinstance(self.scorer, SingleStepReranker):
            raise TypeError

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.log = log
        self.verbose = verbose

    def close_connections(self):
        if self.cachekv is not None:
            self.cachekv.close_connection()

    def clear_traversal_cache(self) -> None:
        return None

    def get_traversal_cache(self) -> None:
        return None

    def calculate_path_score(self, path_len: int, accum_score: float) -> float:
        return accum_score / pow(path_len - 1, self.config.mean_alpha)

    @staticmethod
    def calculate_triplet_score(raw_score: float, max_score_value: float = 10e+5) -> float:
        # Note: в качества скора используется метрика косинусного расстояния [distance]
        # (её нужно вычесть из единицы, чтобы получить метрику косинусной близоси [similarity])

        # Входное значение должно быть определённого типа
        if type(raw_score) in [int, str] or raw_score is None:
            raise ValueError(raw_score, type(raw_score))

        # Входное значение должно быть в заданном диапазоне
        if raw_score < 0.0 or raw_score > 1.0:
            raise ValueError(raw_score)

        # Самостоятельно задаём максимальное значение выходного значения
        if np.abs(1.0 - raw_score) < 10e-10:
            return max_score_value

        return -np.log(1.0 - raw_score)

    def get_available_nodes(self, base_node: NodeInfo, cur_path_idx: int,
                            traversing_paths: List[TraversingPath], prev_node: Union[NodeInfo, None] = None) -> List[NodeInfo]:
        adj_nodes_typedids = set(map(
            lambda node: node.to_str(),
            self.kg_model.graph_struct.db_conn.get_adjecent_nodes(base_node, self.config.accepted_node_types)
        ))
        if prev_node is not None:
            adj_nodes_typedids.discard(prev_node.to_str())

        if not self.config.same_path_intersection_by_node:
            # Удаляем вершины, которые уже есть в текущем пути из числа смежных
            adj_nodes_typedids.difference_update(
                traversing_paths[cur_path_idx].unique_ntypedids)

        if not self.config.diff_paths_intersection_by_node:
            # Удаляем вершины, которые есть в других путях из числа смежных для текущего пути
            for i in range(len(traversing_paths)):
                if i != cur_path_idx:
                    adj_nodes_typedids.difference_update(traversing_paths[i].unique_ntypedids)
        filtered_adjenced_nodes = list(map(lambda n_typedid: from_str_to_nodeinfo(n_typedid), list(adj_nodes_typedids)))
        return filtered_adjenced_nodes

    def get_available_rinfo(
            self, base_node: NodeInfo, adj_nodes: List[NodeInfo], cur_path_idx: int,
            traversing_paths: List[TraversingPath]) -> Tuple[Dict[str, NodeInfo], Dict[str, List[str]]]:

        shared_t_info: Dict[str, NodeInfo] = dict()
        rids_to_tids_map = defaultdict(list)
        for adj_node in adj_nodes:
            tmp_shared_ids = self.kg_model.graph_struct.db_conn.get_nodes_shared_ids(base_node, adj_node, id_type='both')
            tmp_ids_map = {item['t_id']: item['r_id'] for item in tmp_shared_ids}
            cur_tids = set(tmp_ids_map.keys())

            # Удаляем связи, которые уже есть в текущем пути
            tmp_shared_ids: set = cur_tids.difference(traversing_paths[cur_path_idx].unique_tids)

            if not self.config.diff_paths_intersection_by_rel:
                # Удаляем связи, которые уже есть в других путях
                for i in range(len(traversing_paths)):
                    if i != cur_path_idx:
                        tmp_shared_ids.difference_update(traversing_paths[i].unique_tids)

            for t_id in list(tmp_shared_ids):
                shared_t_info[t_id] = adj_node
                rids_to_tids_map[tmp_ids_map[t_id]].append(t_id)

        return shared_t_info, rids_to_tids_map

    def get_triplet_scores(self, query: str, shared_t_info: Dict[str, NodeInfo],
                           rids_to_tids_map: Dict[str, List[str]], batch_size: int = 512) -> List[Tuple[str, NodeInfo, float]]:
        r_ids = list(rids_to_tids_map.keys())
        extended_scores_info = []

        batches = len(r_ids) // batch_size
        batches += 1 if len(r_ids) % batch_size != 0 else 0

        for step in range(batches):
            cur_rids_batch = r_ids[step * batch_size: (step + 1) * batch_size]

            scored_rels = self.scorer.run(
                query=query, top_k=len(cur_rids_batch), includes=[],
                subset_ids=cur_rids_batch, return_with_scores=self.config.vdbname_for_scores
            )

            for raw_score, triplet_info in scored_rels:
                cur_r_id, cur_t_score = (
                    triplet_info.id, BeamSearchTripletsRetriever.calculate_triplet_score(raw_score))
                for t_id in rids_to_tids_map[cur_r_id]:
                    extended_scores_info.append((t_id, shared_t_info[t_id], cur_t_score))

        return extended_scores_info

    @staticmethod
    def extend_tpath(pinfo: TraversingPath, triplet_scores: List[Tuple[str, NodeInfo, float]]) -> List[TraversingPath]:
        # None: у pinfo в path-поле должен лежать минимум один пройденный триплет

        if len(pinfo.path) < 1:
            raise ValueError(pinfo)

        new_tpaths = []
        # добавить новых кандидатов (дополненных вариантов i-ого пути) в пул
        for t_id, new_node, t_score in triplet_scores:
            ext_trpath = deepcopy(pinfo)

            ext_trpath.path.append((ext_trpath.path[-1][2], t_id, new_node))
            ext_trpath.unique_ntypedids.add(new_node.to_str())

            if t_id in ext_trpath.unique_tids:
                raise ValueError(f"Триплет с id '{t_id}' уже существует в пути {ext_trpath}. Все триплеты должны быть уникальными.")

            ext_trpath.unique_tids.add(t_id)
            ext_trpath.accum_score += t_score

            new_tpaths.append(ext_trpath)

        return new_tpaths

    def filter_paths(self, ended_paths: List[TraversedPath],
                     continuous_paths: List[TraversedPath]) -> List[TraversedPath]:
        # Готовим финальный список релевантных путей
        filtered_paths = []
        if self.config.final_sorting_mode == 'continuous_first':
            filtered_paths += sorted(continuous_paths, key=lambda pinfo: pinfo.score)[:self.config.max_paths]
            if len(filtered_paths) < self.config.max_paths:
                num_missed_paths = self.config.max_paths - len(filtered_paths)
                filtered_paths += sorted(ended_paths, key=lambda pinfo: pinfo.score)[:num_missed_paths]

        if self.config.final_sorting_mode == 'ended_first':
            filtered_paths += sorted(ended_paths, key=lambda pinfo: pinfo.score)[:self.config.max_paths]
            if len(filtered_paths) < self.config.max_paths:
                num_missed_paths = self.config.max_paths - len(filtered_paths)
                filtered_paths += sorted(continuous_paths, key=lambda pinfo: pinfo.score)[:num_missed_paths]

        elif self.config.final_sorting_mode == 'mixed':
            filtered_paths = sorted(continuous_paths + ended_paths, key=lambda pinfo: pinfo.score)[:self.config.max_paths]

        else:
            raise KeyError

        return filtered_paths

    def graph_beamsearch(self, query: str, node: NodeInfo) -> List[TraversedPath]:
        traversing_paths = [TraversingPath(
            path=[(None, None, node)], unique_ntypedids={node.to_str()},
            unique_tids=set(), accum_score=0.0)]
        ended_paths = []

        for cur_depth in range(self.config.max_depth):
            self.log(f"Текущая глубина обхода графа: {cur_depth}", verbose=self.verbose)
            self.log(f"Имеющееся количество незавершившихся путей: {len(traversing_paths)}", verbose=self.verbose)
            path_candidates: List[TraversingPath] = list()

            if len(traversing_paths) < 1:
                # прекращаем построение путей, так как больше некуда двигаться
                self.log(f"Больше некуда двигаться. Прекращаем обход графа", verbose=self.verbose)
                break

            opext_s_time = time()
            for i in range(len(traversing_paths)):
                curp_s_time = time()
                cur_path_info = traversing_paths[i]
                prev_node, tail_node = cur_path_info.path[-1][0], cur_path_info.path[-1][2]
                self.log(f"Информация по текущему пути:\n* номер: {i}\n* len: {len(cur_path_info.path)}\n* tail_node: {tail_node}\n* prev_node: {prev_node}", verbose=self.verbose)

                adj_nodes = self.get_available_nodes(tail_node, i, traversing_paths, prev_node)
                self.log(f"Смежные вершины: {len(adj_nodes)}\n", verbose=self.verbose)

                if len(adj_nodes) < 1:
                    self.log("У tail-вершины нет смежных вершин. Считаем путь завершившимся.", verbose=self.verbose)
                    if len(cur_path_info.path) > 1:
                        ended_paths.append(
                            TraversedPath(
                                path=deepcopy(cur_path_info.path),
                                score=self.calculate_path_score(len(cur_path_info.path), cur_path_info.accum_score)
                            )
                        )
                    continue

                shared_t_info, rids_to_tids_map = self.get_available_rinfo(tail_node, adj_nodes, i, traversing_paths)
                if len(shared_t_info) < 1:
                    self.log(
                        "Нет доступных связей для соединения tail-вершины с новой вершиной, Считаем путь завершившимся.", verbose=self.verbose)
                    if len(cur_path_info.path) > 1:
                        ended_paths.append(
                            TraversedPath(
                                path=deepcopy(cur_path_info.path),
                                score=self.calculate_path_score(len(cur_path_info.path), cur_path_info.accum_score)
                            )
                        )
                    continue

                triplet_scores = self.get_triplet_scores(query, shared_t_info, rids_to_tids_map)
                new_tpaths = BeamSearchTripletsRetriever.extend_tpath(traversing_paths[i], triplet_scores)
                self.log(f"Количество новых расширенных путей для текущего пути (до урезания): {len(new_tpaths)}", verbose=self.verbose)
                sorted_new_tpaths = sorted(new_tpaths, key=lambda pinfo: pinfo.accum_score)
                path_candidates += sorted_new_tpaths[:self.config.max_paths]
                self.log(f"Текущее количество путей-кандидатов: {len(path_candidates)}", verbose=self.verbose)
                curp_e_time = time()
                self.log(f"Затраченное время на расширение текущего пути: {curp_e_time - curp_s_time} сек.", verbose=self.verbose)

            opext_e_time = time()

            self.log(f"Количество найденных путей-кандидатов (до урезаний): {len(path_candidates)}", verbose=self.verbose)
            self.log(f"Затраченное суммарное время на текущую итерацию: {opext_e_time-opext_s_time} сек.", verbose=self.verbose)

            # Сортируем (по возрастанию) расширенный список путей
            # по их релевантности и выбираем 'max_paths' лучших
            ordered_candidates = sorted(path_candidates, key=lambda pinfo: pinfo.accum_score)
            traversing_paths = ordered_candidates[:self.config.max_paths]

        self.log(f"Достигнут предел по глубине обхода графа: {self.config.max_depth}", verbose=self.verbose)

        flt_s_time = time()
        continuous_paths = []
        for path_info in traversing_paths:
            continuous_paths.append(
                TraversedPath(
                    path=path_info.path,
                    score=self.calculate_path_score(len(path_info.path), path_info.accum_score)
                )
            )
        filtered_paths = self.filter_paths(ended_paths, continuous_paths)
        flt_e_time = time()

        self.log(f"Финальное количество найденных путей: {len(filtered_paths)}", verbose=self.verbose)
        self.log(f"Затраченнное время на фильтрацию путей: {flt_e_time-flt_s_time} сек.", verbose=self.verbose)

        return filtered_paths

    def get_cache_key(self, query: str, node: NodeInfo) -> List[str]:
        return [self.config.to_str(), query, node.to_str()]

    @CacheUtils.cache_method_output
    def search(self, query: str, node: NodeInfo) -> Tuple[List[Triplet]]:
        paths_info = self.graph_beamsearch(query, node)

        uniques_tids = set()
        for p_info in paths_info:
            # Note: в нулевом кортеже у всех путей
            # только в координате для хранения id конечной вершины
            # не лежит None.
            for triplet_info in p_info.path[1:]:
                uniques_tids.add(triplet_info[1])

        extracted_triplets = self.kg_model.graph_struct.db_conn.read(list(uniques_tids))
        # PAY ATTENTION: tuple is needed to satisfy decorator interface
        return extracted_triplets,

    @accumulate_step_info
    def get_relevant_triplets(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo, bool]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log("RETRIEVER: BeamSearchTripletsRetriever", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        rinfo = ReturnInfo()
        cache_hits: List[bool] = []

        nodes: List[NodeInfo] = []
        unique_ntypedids = set()
        for node in query_info.linked_nodes:
            node_typedid = node.to_str()
            if node_typedid not in unique_ntypedids:
                unique_ntypedids.add(node_typedid)
                nodes.append(node)
        self.log(f"Вершины, для которых будет запущейн BeamSearch: {nodes}", verbose=self.verbose)

        unique_triplets_map: Dict[str, Triplet] = dict()
        for node in nodes:
            self.log(f"Запускаем BeamSearch по вершине: {node}", verbose=self.verbose)
            tmp_triplets, cache_hit = self.search(query_info.query, node)
            cache_hits.append(cache_hit)
            self.log(f"Количество извлечённых триплетов для данной вершины: {len(tmp_triplets)}", verbose=self.verbose)

            for triplet in tmp_triplets:
                unique_triplets_map[triplet.relation.get_typedid()] = triplet
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        self.log(f"Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: {len(unique_triplets)}", verbose=self.verbose)
        relations_counter = Counter([triplet.relation.type for triplet in unique_triplets])
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {relations_counter}", verbose=self.verbose)

        cachehit_summary = (sum(cache_hits) / len(cache_hits)) >= 0.5
        return unique_triplets, rinfo, cachehit_summary
