from dataclasses import dataclass, field
from typing import List, Dict, Set, Union, Tuple
import math
from tqdm import tqdm
from copy import deepcopy
from collections import defaultdict
import torch

from .config import NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING, TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING, \
    EMBEDDINGS_MODEL_LOG_PATH
from ...db_drivers.vector_driver import VectorDriverConfig, VectorDBInstance
from ...db_drivers.vector_driver.embedders import EmbedderModel
from ...db_drivers.vector_driver.VectorComposer import VectorComposer
from ...utils.data_structs import Triplet, TripletCreator, NodeCreator
from ...utils import Logger, NodeType


@dataclass
class EmbeddingsModelConfig:
    """Конфигурация векторной структуры данных.

    :param nodesdb_driver_configs_mapping: Словарь с именованными конфигурациями коннекторов к векторным базам данных, которые отвечают за хранение различных векторных представлений вершин из графовой структуры. Значение по умолчанию NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING.
    :type nodesdb_driver_configs_mapping: Dict[str, VectorDriverConfig], optional
    :param tripletsdb_driver_configs_mapping: Словарь с именованными конфигурациями коннекторов к векторным базам данных, которые отвечают за хранение различных векторных представлений триплетов из графовой структуры.  Значение по умолчанию TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING.
    :type tripletsdb_driver_configs_mapping: Dict[str, VectorDriverConfig], optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(EMBEDDINGS_MODEL_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    nodesdb_driver_configs_mapping: Dict[str, VectorDriverConfig] = field(
        default_factory=lambda: NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING)
    tripletsdb_driver_configs_mapping: Dict[str, VectorDriverConfig] = field(
        default_factory=lambda: TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING)

    log: Logger = field(default_factory=lambda: Logger(EMBEDDINGS_MODEL_LOG_PATH))
    verbose: bool = False


class EmbeddingsModel:
    """Структура данных для хранения информации в векторном формате.

    :param embedders_mapping: Словарь с именованными коннекторами к embedder-моделям для получения векторных представлений текста. Название embedder-модели должно соответствовать названию конфигурации коннектора к векторной бд из 'nodesdb_driver_configs_mapping'- и 'tripletsdb_driver_configs_mapping'-полей, к которой она относится.
    :type embedders_mapping: Dict[str,EmbedderModel]
    :param config: Конфигурация векторной структуры данных. Значение по умолчанию EmbeddingsModelConfig().
    :type config: EmbeddingsModelConfig, optional
    """

    def __init__(self, embedders_mapping: Dict[str, EmbedderModel], config: EmbeddingsModelConfig = EmbeddingsModelConfig()):
        self.config = config

        self.triplets_vectordbs: VectorComposer = VectorComposer(
            self.config.tripletsdb_driver_configs_mapping, embedders_mapping)

        # Создаём наборй векторных бд для вершины каждого типа в отдельности
        self.nodes_vectordbs: Dict[NodeType, VectorComposer] = {}
        nodes_types = [NodeType.object, NodeType.hyper, NodeType.episodic]
        for node_type in nodes_types:
            modified_configs: Dict[str, VectorDriverConfig] = deepcopy(self.config.nodesdb_driver_configs_mapping)
            for m_config in modified_configs.values():
                m_config.db_config.db_info['table'] += f"_{node_type.value}"
            self.nodes_vectordbs[node_type] = VectorComposer(modified_configs, embedders_mapping)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def check_consistency(self) -> bool:
        for v_composer in self.nodes_vectordbs.values():
            v_composer.check_consistency()
        self.triplets_vectordbs.check_consistency()

    def create_triplets(self, triplets: List[Triplet], create_nodes: bool = True,
                        batch_size: int = 128, status_bar: bool = True) -> Dict[str, Set[str]]:
        """Метод предназначен для добавления информации, представленной в виде списка триплетов, в векторную структуру.
        Триплеты-дубликаты (по строковому представлению) в структуру не добавляются.

        :param triplets: Набор триплетов для добавления в векторную структуру.
        :type triplets: List[Triplet]
        :param create_nodes: Если True, то в векторную структуру отдельно также будут добавлены вершины из триплетов. Вершины-дубликаты (по строковому представлению) не добавляются (отбрасываются), иначе False. Значение по умолчанию True.
        :type create_nodes: bool, optional
        :param batch_size: Количество триплетов, которое за одну create-операцию будет добавляться в векторную структуру. Значение по умолчанию 128.
        :type batch_size: int, optional
        :param status_bar: Если True, то в stdout будет записываться прогресс операции (количество обработанных триплетов), иначе False. Значение по умолчанию True.
        :type status_bar: boll, optional
        """
        self.log("Adding triples to vector-model...", verbose=self.verbose)
        unique_relation_ids, unique_node_ids = set(), set()
        existed_relation_ids, existed_node_ids = set(), set()

        batch_count = math.ceil(len(triplets) / batch_size)
        process = tqdm(range(batch_count)
                       ) if status_bar else range(batch_count)
        for batch_idx in process:
            relations_info: List[VectorDBInstance] = list()
            grouped_nodes_info: Dict[NodeType, List[VectorDBInstance]] = defaultdict(list)

            for triplet_idx in range(batch_idx * batch_size, (batch_idx + 1) * batch_size):
                if triplet_idx >= len(triplets):
                    break

                cur_triplet = triplets[triplet_idx]
                cur_rel_id = cur_triplet.relation.id
                _, triplet_str = TripletCreator.stringify(
                    cur_triplet) if cur_triplet.stringified is None else (None, cur_triplet.stringified)
                if cur_rel_id not in unique_relation_ids:
                    unique_relation_ids.add(cur_rel_id)
                    if ((cur_rel_id not in existed_relation_ids) and (not self.triplets_vectordbs.item_exist(cur_rel_id))):
                        existed_relation_ids.add(cur_rel_id)
                        relations_info.append(VectorDBInstance(
                            id=cur_triplet.relation.id, document=triplet_str,
                            metadata={'t_id': cur_triplet.id, 'id': cur_triplet.relation.id}))

                if create_nodes:
                    self.log(
                        "\t- Also adding triplet-nodes in vector-model", verbose=self.verbose)
                    for node in [cur_triplet.start_node, cur_triplet.end_node]:
                        if node.id not in unique_node_ids:
                            unique_node_ids.add(node.id)
                            _, node_str = NodeCreator.stringify(
                                node) if node.stringified is None else (None, node.stringified)
                            if ((node.id not in existed_node_ids) and (not self.nodes_vectordbs[node.type].item_exist(node.id))):
                                existed_node_ids.add(node.id)
                                grouped_nodes_info[node.type].append(VectorDBInstance(
                                    id=node.id, document=node_str, metadata={'id': node.id}))

            grouped_nodes_info = dict(grouped_nodes_info)
            if len(grouped_nodes_info) == 0:
                grouped_nodes_info = None

            self.create_stringified_triplets(relations_info, grouped_nodes_info)

        self.log(
            f"all/unique/existed relations - {len(triplets)}/{len(unique_relation_ids)}/{len(existed_relation_ids)}", verbose=self.verbose)
        self.log(
            f"all/unique/existed nodes - {len(triplets)*2}/{len(unique_node_ids)}/{len(existed_node_ids)}", verbose=self.verbose)
        self.log("Triples were successfully added to vector-model!",
                 verbose=self.verbose)
        return {'nodes': existed_node_ids, 'triplets': existed_relation_ids}

    def create_stringified_triplets(self, relations_info: List[VectorDBInstance],
                                    grouped_nodes_info: Union[None, Dict[NodeType, List[VectorDBInstance]]] = None) -> None:
        """Метод предназначен для добавления строковых представлений триплетов/вершин в векторную структуру.

        :param relations_info: Список кортежей с информацие о триплетах, которые будут добавляться в embeddings-модель. В каждый кортеж входит следующая информация: (1) идентификатор триплетов, с которым он будет сохранен, (2) строковое представление триплета и (3) метаданные.
        :type relations_info: List[VectorDBInstance]
        :param grouped_nodes_info: Сгруппированные (по типу вершин) списки кортежей с информацие о вершинах, которые будут добавляться в embeddings-модель. В каждый кортеж входит следующая информация: (1) идентификатор вершины, с которым она будет сохранена, (2) строковое представление вершины и (3) метаданные.
        :type grouped_nodes_info: Union[None,Dict[NodeType, List[VectorDBInstance]]], optional
        """
        if len(relations_info):
            self.create_instances('relations', relations_info)
        if grouped_nodes_info is not None:
            for node_type, nodes_instances in grouped_nodes_info.items():
                self.create_instances('nodes', nodes_instances, cat_type=node_type)

    def create_instances(self, db_type: str, instances: List[VectorDBInstance], cat_type: Union[NodeType, None] = None) -> None:
        """Метод предназначен для добавления набора объектов в одно из хранилищ данных векторной структуры: для триплетов или вершин.

        :param db_type: Тип хранилища, в которое нужно добавить объекты. Принимает значение "triplets" или "nodes".
        :type db_type: str
        :param instances: Список добавляемых объектов.
        :type instances: List[VectorDBInstance]
        :param cat_type: Категория добавляемых объектов. Данный параметр должен использоваться при добавлении nodes-объектов; для указания их типа. Значение по умолчанию None.
        :type cat_type: Union[NodeType, None], optional
        """
        torch.cuda.empty_cache()
        if db_type == 'nodes':
            self.nodes_vectordbs[cat_type].create(instances)
        elif db_type == 'relations':
            self.triplets_vectordbs.create(instances)
        else:
            raise ValueError

    def delete_triplets(self, triplets: List[Triplet], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из векторной структуры.

        :param triplets: Набор триплетов на удаление.
        :type triplets: List[Triplet]
        :param delete_info: Информация для векторной структуры, чтобы удалить конкретные вершины/триплеты и сохранить консистентность модели графа знаний.
        :type delete_info: Union[None, List[Dict[str,bool]]], optional
        """
        unique_relation_ids = set()
        grouped_unique_node_ids: Dict[NodeType, Set[str]] = defaultdict(set)
        for i, triplet in enumerate(triplets):
            cur_info = delete_info.get(i, None)

            if (cur_info is None) or cur_info['triplet']:
                unique_relation_ids.add(triplet.relation.id)

            if (cur_info is None) or cur_info['s_node']:
                grouped_unique_node_ids[triplet.start_node.type].add(triplet.start_node.id)

            if (cur_info is None) or cur_info['e_node']:
                grouped_unique_node_ids[triplet.end_node.type].add(triplet.end_node.id)

        grouped_unique_node_ids = dict(grouped_unique_node_ids)
        if len(grouped_unique_node_ids) > 0:
            grouped_unique_node_ids = {k: list(v) for k, v in grouped_unique_node_ids.items()}
        else:
            grouped_unique_node_ids = None

        unique_relation_ids = list(unique_relation_ids)

        self.delete_stringified_triplets(unique_relation_ids, grouped_unique_node_ids)

    def delete_stringified_triplets(self, relation_ids: List[str], grouped_node_ids: Union[None, Dict[NodeType, Set[str]]] = None) -> None:
        """Метод предназначен для удаления строковых представлений триплетов/вершин из векторной структуры.

        :param relation_ids: Идентификаторы триплетов (связей) на удаление.
        :type relation_ids: List[str]
        :param grouped_node_ids: Сгруппированный (по типу вершин) набор идентификаторов вершин на удаление. Значение по умолчанию None.
        :type grouped_node_ids: Union[None, Dict[NodeType, Set[str]]], optional
        """
        self.delete_instances('relations', relation_ids)
        if grouped_node_ids is not None:
            for node_type, node_ids in grouped_node_ids.items():
                self.delete_instances('nodes', ids=node_ids, cat_type=node_type)

    def delete_instances(self, db_type: str, ids: List[str], cat_type: Union[None, NodeType] = None) -> None:
        """Метод предназначен для удаления набора объектов из определённой бд векторной структуры: из бд с триплетами или вершинами.

        :param db_type: Тип бд, из которой нужно удалить объекты. Принимает значение "triplets" или "nodes".
        :type db_type: str
        :param ids: Идентификаторы объектов на удаление из бд.
        :type ids: List[str]
        :param cat_type: Категория удаляемых объектов. Данный параметр должен использоваться при удалении nodes-объектов; для указания их типа. Значение по умолчанию None.
        :type cat_type: Union[NodeType, None], optional
        """
        if db_type == 'nodes':
            self.nodes_vectordbs[cat_type].delete(ids)
        elif db_type == 'relations':
            self.triplets_vectordbs.delete(ids)

    def read_embbeddings(self, db_type: str, ids: List[str], cat_type: Union[None, NodeType] = None) -> List[List[float]]:
        """Метод предназначен для получения векторных представлений объектов из определённой бд векторной структуры: из бд с триплетами или вершинами.

        :param db_type: Тип бд, в которой осуществляется поиск векторных представлений для заданных объектов. Принимает значение "triplets" или "nodes".
        :type db_type: str
        :param ids: Идентификаторы объектов, для которых необходимо получить векторные представления.
        :type ids: List[str]
        :return: Список полученных векторных представлений для заданных объектов.
        :rtype: List[List[float]]
        :param cat_type: Категория объектов. Данный параметр должен использоваться при попытке получения nodes-объектов; необходимо указания их тип. Значение по умолчанию None.
        :type cat_type: Union[NodeType, None], optional
        """
        if db_type == 'nodes':
            instances = self.nodes_vectordbs[cat_type].read(ids, includes=['embeddings'])
        elif db_type == 'triplets':
            instances = self.triplets_vectordbs.read(ids, includes=['embeddings'])
        else:
            raise ValueError

        embeddings = list(map(lambda inst: inst.embedding, instances))
        return embeddings

    def count_items(self, detailed: bool = False) -> Dict[str, int]:
        self.check_consistency()
        nodes_count = {n_type.value: v_composer.count_items() for n_type, v_composer in self.nodes_vectordbs.items()}
        if not detailed:
            nodes_count = sum([list(v_counts.values())[0] for _, v_counts in nodes_count.items()])

        triplets_count = self.triplets_vectordbs.count_items()
        if not detailed:
            triplets_count = list(triplets_count.values())[0]

        return {'nodes': nodes_count, 'triplets': triplets_count}

    def clear(self) -> None:
        """Метод предназначен для удаления содержимого векторной структуры данных.
        """
        for n_type in self.nodes_vectordbs.keys():
            self.nodes_vectordbs[n_type].clear()
        self.triplets_vectordbs.clear()

    def __del__(self):
        for n_type in self.nodes_vectordbs.keys():
            self.nodes_vectordbs[n_type].close_connection()
        self.triplets_vectordbs.close_connection()
