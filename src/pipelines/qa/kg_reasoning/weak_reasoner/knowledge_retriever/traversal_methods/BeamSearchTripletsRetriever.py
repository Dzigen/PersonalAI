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

from .configs import BSGS_RERANKDRIVER_DEFAULT_CONFIG, BEAMSEARCH_RETRIEVER_LOG_PATH
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, NodeType, NodeInfo, TripletInfo, RelationInfo, from_str_to_nodeinfo
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
    :param max_depth: Максимальная глубина построенных/пройденных путей. Значение по умолчанию 3.
    :type max_depth: int, optional
    :param max_paths: Максимальное количество построенных/пройденных путей. Значение по умолчанию 18.
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
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы BeamSearchTripletsRetriever-класса. Значение по умолчанию 'qa_beamsearch_t_retriever_cache'.
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
        default_factory=lambda: [NodeType.object, NodeType.hyper, NodeType.episodic])  # NodeType.time
    final_sorting_mode: str = 'mixed'  # 'ended_first' | 'mixed' | 'continuous_first'

    cache_table_name: str = 'qa_beamsearch_t_retriever_cache'
    log_path: str = BEAMSEARCH_RETRIEVER_LOG_PATH

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
    :param search_config: Конфигурация BeamSearchTripletsRetriever-алгоритма. Значение по умолчанию GraphBeamSearchConfig().
    :type search_config: Union[GraphBeamSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel,
                 search_config: Union[GraphBeamSearchConfig, Dict] = GraphBeamSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
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

        self.log = Logger(search_config.log_path)
        self.verbose = search_config.verbose
        self.log_level = search_config.log_level

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

    def filter_nodes_typedids(self, adjacent_nodes_typedids: List[str], cur_path_idx: int,
                              traversing_paths: List[TraversingPath], prev_node: Union[NodeInfo, None] = None) -> List[NodeInfo]:
        adj_nodes_typedids: Set[str] = set(adjacent_nodes_typedids)
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
                    adj_nodes_typedids.difference_update(
                        traversing_paths[i].unique_ntypedids)
        filtered_adjacent_nodes = list(adj_nodes_typedids)
        return filtered_adjacent_nodes

    def filter_relations_tids(self, incid_relations_tids: List[str], cur_path_idx: int,
                              traversing_paths: List[TraversingPath]) -> List[str]:
        tids = set(incid_relations_tids)

        # Удаляем связи, которые уже есть в текущем пути
        filtered_tids: Set[str] = tids.difference(traversing_paths[cur_path_idx].unique_tids)

        if not self.config.diff_paths_intersection_by_rel:
            # Удаляем связи, которые уже есть в других путях
            for i in range(len(traversing_paths)):
                if i != cur_path_idx:
                    filtered_tids.difference_update(traversing_paths[i].unique_tids)

        return list(filtered_tids)

    def get_available_triples_info(
        self, base_node: NodeInfo, cur_path_idx: int,
        traversing_paths: List[TraversingPath], prev_node: Union[NodeInfo, None] = None)\
            -> Tuple[Union[None, Dict[str, NodeInfo]], Union[None, Dict[str, List[str]]], bool]:

        shared_t_info: Dict[str, NodeInfo] = dict()
        rids_to_tids_map: Dict[str, List[str]] = defaultdict(list)

        incident_triples: List[TripletInfo] = \
            self.kg_model.graph_struct.db_conn.get_incident_triples(
                base_node, accepted_n_types=self.config.accepted_node_types)
        self.log.debug(f"Количество инцидентных триплетов к вершине {base_node}: {len(incident_triples)}",
                       verbose=self.verbose, log_level=self.log_level)

        #
        adjn_to_incidr_map: Dict[str, List[Tuple[str, RelationInfo]]] = defaultdict(list)
        basenode_str = base_node.to_str()
        for triple_info in incident_triples:
            if triple_info.start_node.to_str() != basenode_str:
                adjn_to_incidr_map[triple_info.start_node.to_str()].append(
                    (triple_info.id, triple_info.relation))
            else:
                adjn_to_incidr_map[triple_info.end_node.to_str()].append(
                    (triple_info.id, triple_info.relation))
        adjn_to_incidr_map = dict(adjn_to_incidr_map)

        filtered_adjacent_nodes_typedids: List[str] = self.filter_nodes_typedids(
            list(adjn_to_incidr_map.keys()), cur_path_idx, traversing_paths, prev_node)
        self.log.debug(f"Количество смежных вершин к {base_node} после фильтрации: {len(filtered_adjacent_nodes_typedids)}",
                       verbose=self.verbose, log_level=self.log_level)

        if len(filtered_adjacent_nodes_typedids) < 1:
            return shared_t_info, rids_to_tids_map, True

        #
        incidr_to_adjn_map: Dict[str, Tuple[str, NodeInfo]] = dict()
        for node_typedid in filtered_adjacent_nodes_typedids:
            cur_nodeinfo = from_str_to_nodeinfo(node_typedid)
            for incident_relation in adjn_to_incidr_map[node_typedid]:
                incidr_to_adjn_map[incident_relation[0]] = (incident_relation[1].id, cur_nodeinfo)

        filtered_incident_relations_tids: List[str] = self.filter_relations_tids(
            list(incidr_to_adjn_map.keys()), cur_path_idx, traversing_paths)
        self.log.debug(f"Количество инцидентных отношений к вершине {base_node} после фильтрации: {len(filtered_incident_relations_tids)}",
                       verbose=self.verbose, log_level=self.log_level)

        #
        for t_id in filtered_incident_relations_tids:
            shared_t_info[t_id] = incidr_to_adjn_map[t_id][1]
            rids_to_tids_map[incidr_to_adjn_map[t_id][0]].append(t_id)
        rids_to_tids_map = dict(rids_to_tids_map)

        return shared_t_info, rids_to_tids_map, False

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
            self.log.debug("Текущая глубина обхода графа: %d", cur_depth, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("Имеющееся количество незавершившихся путей: %d", len(traversing_paths), verbose=self.verbose, log_level=self.log_level)
            path_candidates: List[TraversingPath] = list()

            if len(traversing_paths) < 1:
                # прекращаем построение путей, так как больше некуда двигаться
                self.log.warning("Больше некуда двигаться. Прекращаем обход графа", verbose=self.verbose, log_level=self.log_level)
                break

            opext_s_time = time()
            for i in range(len(traversing_paths)):
                curp_s_time = time()
                cur_path_info = traversing_paths[i]
                prev_node, tail_node = cur_path_info.path[-1][0], cur_path_info.path[-1][2]
                self.log.debug("Информация по текущему пути:\n* номер: %d\n* len: %d\n* tail_node: %s\n* prev_node: %s",
                               i, len(cur_path_info.path), tail_node, prev_node, verbose=self.verbose, log_level=self.log_level)

                shared_t_info, rids_to_tids_map, is_zeroadj_nodes = self.get_available_triples_info(
                    tail_node, i, traversing_paths, prev_node)

                if is_zeroadj_nodes:
                    self.log.debug("У tail-вершины нет смежных вершин. Считаем путь завершившимся.",
                                   verbose=self.verbose, log_level=self.log_level)
                    if len(cur_path_info.path) > 1:
                        ended_paths.append(
                            TraversedPath(
                                path=deepcopy(cur_path_info.path),
                                score=self.calculate_path_score(len(cur_path_info.path), cur_path_info.accum_score)
                            )
                        )
                    continue

                if len(shared_t_info) < 1:
                    self.log.debug(
                        "Нет доступных связей для соединения tail-вершины с новой вершиной, Считаем путь завершившимся.",
                        verbose=self.verbose, log_level=self.log_level)
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
                self.log.debug("Количество новых расширенных путей для текущего пути (до урезания): %d", len(new_tpaths), verbose=self.verbose, log_level=self.log_level)
                sorted_new_tpaths = sorted(new_tpaths, key=lambda pinfo: pinfo.accum_score)
                path_candidates += sorted_new_tpaths[:self.config.max_paths]
                self.log.debug("Текущее количество путей-кандидатов: %d", len(path_candidates), verbose=self.verbose, log_level=self.log_level)
                curp_e_time = time()
                self.log.debug("Затраченное время на расширение текущего пути: %.5f сек", curp_e_time - curp_s_time, verbose=self.verbose, log_level=self.log_level)

            opext_e_time = time()

            self.log.debug("Количество найденных путей-кандидатов (до урезаний): %d", len(path_candidates), verbose=self.verbose, log_level=self.log_level)
            self.log.debug("Затраченное суммарное время на текущую итерацию: %.5f сек", opext_e_time - opext_s_time, verbose=self.verbose, log_level=self.log_level)

            # Сортируем (по возрастанию) расширенный список путей
            # по их релевантности и выбираем 'max_paths' лучших
            ordered_candidates = sorted(path_candidates, key=lambda pinfo: pinfo.accum_score)
            traversing_paths = ordered_candidates[:self.config.max_paths]

        self.log.debug("Достигнут предел по глубине обхода графа: %d", self.config.max_depth, verbose=self.verbose, log_level=self.log_level)

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

        self.log.debug("Финальное количество найденных путей: %d", len(filtered_paths), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Затраченнное время на фильтрацию путей: %.5f сек", flt_e_time - flt_s_time, verbose=self.verbose, log_level=self.log_level)

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
        self.log.debug("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Retriever: BeamSearchTripletsRetriever", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query_info.query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s", query_info.query, verbose=self.verbose, log_level=self.log_level)

        rinfo = ReturnInfo()
        cache_hits: List[bool] = []

        nodes: List[NodeInfo] = []
        unique_ntypedids = set()
        for node in query_info.linked_nodes:
            node_typedid = node.to_str()
            if node_typedid not in unique_ntypedids:
                unique_ntypedids.add(node_typedid)
                nodes.append(node)
        self.log.debug("Вершины, для которых будет запущейн BeamSearch: %s", nodes, verbose=self.verbose, log_level=self.log_level)

        unique_triplets_map: Dict[str, Triplet] = dict()
        for node in nodes:
            self.log.debug("Запускаем BeamSearch по вершине: %s", node, verbose=self.verbose, log_level=self.log_level)
            tmp_triplets, cache_hit = self.search(query_info.query, node)
            cache_hits.append(cache_hit)
            self.log.debug("Количество извлечённых триплетов для данной вершины: %d", len(tmp_triplets), verbose=self.verbose, log_level=self.log_level)

            for triplet in tmp_triplets:
                unique_triplets_map[triplet.relation.get_typedid()] = triplet
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        self.log.debug("Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: %d", len(unique_triplets), verbose=self.verbose, log_level=self.log_level)
        relations_counter = Counter([triplet.relation.type for triplet in unique_triplets])
        self.log.debug("Распределение типов связей в наборе извлечённых триплетов: %s", relations_counter, verbose=self.verbose, log_level=self.log_level)

        cachehit_summary = (sum(cache_hits) / len(cache_hits)) >= 0.5 if len(cache_hits) > 0 else False
        return unique_triplets, rinfo, cachehit_summary
