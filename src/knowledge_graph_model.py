from dataclasses import dataclass, field
from typing import List, Dict
import math
import json
from tqdm import tqdm

from .db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriver, VectorDriverConfig, VectorDBInstance
from .db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from .db_drivers.graph_driver import GraphDriver, GraphDriverConfig, DEFAULT_NEO4J_CONFIG
from .utils.data_structs import Triplet, TripletCreator, NodeCreator
from .utils import Logger

NODES_DB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        path="../data/graph_structures/vectorized_nodes/default_densedb", db_info={'db': 'default_db', 'table': "vectorized_nodes"}))
TRIPLETS_DB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        path="../data/graph_structures/vectorized_triplets/default_densedb", db_info={'db': 'default_db', 'table': "vectorized_nodes"}))

EMBEDDINGS_MODEL_LOG_PATH = 'log/em'

@dataclass
class EmbeddingsModelConfig:
    """Конфигурация векторной модели данных.

    :param nodesdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений вершин из графовой модели.
    :type nodesdb_driver_config: VectorDriverConfig
    :param tripletsdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений триплетов из графовой модели.
    :type tripletsdb_driver_config: VectorDriverConfig
    :param tripletsdb_driver_config: Конфигурация класса, отвечающего за приведения текста в его векторрное представление с помощью embedder-модели.
    :type embedder_config: EmbedderModelConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения комопненты.
    :type log: Logger
    :param verbose: Если, True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл.
    :type verbose: bool
    """
    nodesdb_driver_config: VectorDriverConfig = field(default_factory=lambda: NODES_DB_DEFAULT_DRIVER_CONFIG)
    tripletsdb_driver_config: VectorDriverConfig = field(default_factory=lambda: TRIPLETS_DB_DEFAULT_DRIVER_CONFIG)
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())
    log: Logger = field(default_factory=lambda: Logger(EMBEDDINGS_MODEL_LOG_PATH))
    verbose: bool = False

class EmbeddingsModel:
    """Модель хранения информации в векторной структуре данных.

    :param config: Конфигурация векторного хранилища.
    :type config: EmbeddingsModelConfig
    """
    def __init__(self, config: EmbeddingsModelConfig = EmbeddingsModelConfig()):
        self.config = config
        self.log = config.log
        self.vectordbs = {
            'nodes': VectorDriver.connect(config.nodesdb_driver_config),
            'triplets': VectorDriver.connect(config.tripletsdb_driver_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def create_triplets(self, triplets:List[Triplet], create_nodes:bool=True, batch_size:int=128)-> None:
        """Метод предназначен для добавления информации, представленной в виде списка триплетов, в модель.
        Триплеты-дубликаты (по строковому) представлению в хранилище не добавляются.

        :param triplets: Набор триплетов для добавления в векторную модель данных.
        :type triplets: List[Triplet]
        :param create_nodes: Если True, то в векторную модель отдельно также будут добавлены вершины из триплетов. Вершины-дубликаты (по строковому представлению) не добавляются (отбрасываются), иначе False. Defaults to True.
        :type create_nodes: bool, optional
        :param batch_size: Количество триплетов, которое за одну create-операцию добавляются в модель. Defaults to 128.
        :type batch_size: int, optional
        """
        self.log("Adding triples to vector-model...", verbose=self.config.verbose)
        unique_relation_ids, unique_node_ids = set(), set()
        existed_relation_ids, existed_node_ids = set(), set()

        batch_count = math.ceil(len(triplets) / batch_size)
        for batch_idx in tqdm(range(batch_count)):
            relation_ids, relation_strs = list(), list()
            node_ids, node_strs = list(), list()

            for triplet_idx in range(batch_idx*batch_size, (batch_idx+1)*batch_size):
                if triplet_idx >= len(triplets):
                    break

                cur_triplet = triplets[triplet_idx]
                cur_rel_id = cur_triplet.relation.id
                _, triplet_str =  TripletCreator.stringify(cur_triplet) if cur_triplet.stringified is None else (None, cur_triplet.stringified)
                if cur_rel_id not in unique_relation_ids:
                    unique_relation_ids.add(cur_rel_id)
                    if ((cur_rel_id not in existed_relation_ids) and (not self.vectordbs['triplet'].item_exist(cur_rel_id))):
                        existed_relation_ids.add(cur_rel_id)
                        relation_ids.append(cur_triplet.relation.id)
                        relation_strs.append(triplet_str)

                if create_nodes:
                    self.log("\t- Also adding triplet-nodes in vector-model", verbose=self.config.verbose)
                    for node in [cur_triplet.start_node, cur_triplet.end_node]:
                        if node.id not in unique_node_ids:
                            unique_node_ids.add(node.id)
                            _, node_str = NodeCreator.stringify(node) if node.stringified is None else (None, node.stringified)
                            if ((node.id not in existed_relation_ids) and (not self.vectordbs['node'].item_exist(node.id))):
                                existed_node_ids.add(node.id)
                                node_ids.append(node.id)
                                node_strs.append(node_str)

            self.create_stringified_triplets(relation_ids, relation_strs, node_ids, node_strs)

        self.log(f"all/unique/existed relations - {len(triplets)}/{len(unique_relation_ids)}/{len(existed_relation_ids)}", verbose=self.config.verbose)
        self.log(f"all/unique/existed nodes - {len(triplets)*2}/{len(unique_node_ids)}/{len(existed_node_ids)}", verbose=self.config.verbose)
        self.log("Triples were successfully added to vector-model!", verbose=self.config.verbose)

    def delete_triplets(self, triplets: List[Triplet], delete_nodes: bool = True) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из модели.

        :param triplets: Набора триплетов для удаления.
        :type triplets: List[Triplet]
        :param delete_nodes: Если True, то из векторной модели также будут удалены вершины, которые принадлежат данных триплета, иначе False, Defaults to True
        :type delete_nodes: bool, optional
        """
        triplets_ids = list(map(lambda v: v.id, triplets))

        unique_nodes_ids = None
        if delete_nodes:
            nodes_ids = []
            nodes_ids += [triplet.start_node.id for triplet in triplets]
            nodes_ids += [triplet.end_node.id for triplet in triplets]
            unique_nodes_ids = list(set(nodes_ids))

        self.delete_stringified_triplets(triplets_ids, unique_nodes_ids)

    def create_stringified_triplets(self, triplets_ids: List[str], stringified_triplets: List[str],
                     nodes_ids: List[str] = None, stringified_nodes: List[str] = None) -> None:
        """Метод предназначен для добавления строковых представлений триплетов/вершин в векторную модель.

        :param triplets_ids: Идентификаторы триплетов, с которыми они будут сохранены в моделе.
        :type triplets_ids: List[str]
        :param stringified_triplets: Строковые представления триплетов для сохранения в моделе.
        :type stringified_triplets: List[str]
        :param nodes_ids: Идентификаторы верщин, с которыми они будут сохранены в моделе. Defaults to None.
        :type nodes_ids: List[str], optional
        :param stringified_nodes: Строковые представления вершин для сохранения в моделе. Defaults to None.
        :type stringified_nodes: List[str], optional
        """
        if len(triplets_ids):
            self.create_instances('triplets', triplets_ids, stringified_triplets)
        if nodes_ids is not None and len(nodes_ids):
            self.create_instances('nodes', nodes_ids, stringified_nodes)

    def delete_stringified_triplets(self, triplets_ids: List[str], nodes_ids: List[str] = None) -> None:
        """Метод предназначен для удаления строковых представлений триплетов/вершин из векторной модели.

        :param triplets_ids: Идентификаторы триплетов на удаление из модели.
        :type triplets_ids: List[str]
        :param nodes_ids: Идентификаторы вершин на удаление из модели. Defaults to None
        :type nodes_ids: List[str], optional
        """
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)

    def create_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]) -> None:
        """Метод предназанчен для добавления набора объектов в одно их хранилищ данных векторной модели: для триплетов или вершин.

        :param db_type: Тип хранилища, в которое нужно добавить объекты. Принимает значение "triplets" или "nodes".
        :type db_type: str
        :param ids: Идентификаторы объектов, с которыми они будут добавлены в хранилище.
        :type ids: List[str]
        :param stringified_instances: Строковые представления объектов, которые будут сохранены в хранилище.
        :type stringified_instances: List[str]
        """
        embs = self.embedder.encode_passages(stringified_instances)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb, metadata={'id': id})
                            for id, doc, emb in zip(ids, stringified_instances, embs)]
        self.vectordbs[db_type].create(formated_instances)

    def delete_instances(self, db_type: str, ids: List[str]) -> None:
        """Метод предназанчен для удаления набора объектов из определённого хранилища данных векторной модели: из хранилища триплетов или вершин.

        :param db_type: Тип хранилища, из которого нужно удалить объекты. Принимает значение "triplets" или "nodes".
        :type db_type: str
        :param ids: Идентификаторы объектов на удаление из хранилища.
        :type ids: List[str]
        """
        self.vectordbs[db_type].delete(ids)

    def read_embbeddings(self, db_type: str, ids: List[str]) -> List[List[float]]:
        """Метод предназначен для получения векторных представлений объектов из определённого хранилища векторной модели: из хранилища триплетов или вершин.

        :param db_type: Тип хранилища, в котором осуществялется поиск векторных представлений для заданных объектов. Принимает значени "triplets" или "nodes".
        :type db_type: str
        :param ids: Идентификаторы объектов, для которых необходимо получить векторные представления.
        :type ids: List[str]
        :return: Список полученных векторных представлений для заданных объектов.
        :rtype: List[List[float]]
        """
        instances = self.vectordbs[db_type].read(ids, includes=['embeddings'])
        embeddings = list(map(lambda inst: inst.embedding, instances))
        return embeddings

GRAPH_DB_DEFAULT_DRIVER_CONFIG = GraphDriverConfig(db_vendor='neo4j', db_config=DEFAULT_NEO4J_CONFIG)
GRAPH_MODEL_LOG_PATH = 'log/gm'

@dataclass
class GraphModelConfig:
    """Конфигруация графовой модели.

    :param driver_config: Конфигурация графового хранилища данных.
    :type driver_config: GraphDriverConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения комопненты.
    :type log: Logger
    :param verbose: Если, True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл.
    :type verbose: bool
    """
    driver_config: GraphDriverConfig = field(default_factory=lambda: GRAPH_DB_DEFAULT_DRIVER_CONFIG)
    log: Logger = field(default_factory=lambda: Logger(GRAPH_MODEL_LOG_PATH))
    verbose: bool = False

class GraphModel:
    """Модель хранения информации в графовой структуре данных.

    :param config: Конфигурация графовой модели.
    :type config: GraphModelConfig
    """
    def __init__(self, config: GraphModelConfig = GraphModelConfig()) -> None:
        self.config = config
        self.log = config.log
        self.db_conn = GraphDriver.connect(self.config.driver_config)

    def create_triplets(self, triplets: List[Triplet], batch_size: int = 64) -> None:
        """Метод предназначен для сохранения информации, представленной в виде списка триплетов, в модель.

        :param triplets: Набора триплетов для добавления в графовое хранилище
        :type triplets: List[Triplet]
        :param batch_size: Количество триплетов, которое за одну create-операцию добавляется в хранилище. Defaults to 64.
        :type batch_size: int, optional
        """
        self.log("Adding triplets to graph-model...", verbose=self.config.verbose)
        unique_triplet_ids, unique_node_ids = set(), set()
        existed_triplet_ids, existed_node_ids = set(), set()

        batches = math.ceil(len(triplets) / batch_size)
        for batch_idx in tqdm(range(batches)):
            # if n1 rel n2
            # else empty
                # n1 _ _
                # _ _ n2
                # n1 _ n2
                # _ _ _

            creation_info = dict()
            triplets_to_create = list()
            info_counter = -1
            for triplet_idx in range(batch_idx*batch_size, (batch_idx+1)*batch_size, 1):
                if triplet_idx >= len(triplets):
                    break

                cur_triplet = triplets[triplet_idx]
                if ((cur_triplet.id not in unique_triplet_ids) and (not self.db_conn.item_exist(cur_triplet.id, id_type='triplet'))):
                    unique_triplet_ids.add(cur_triplet.id)
                    triplets_to_create.append(cur_triplet)
                    info_counter += 1
                    creation_info[info_counter] = {'s_node': False, 'e_node': False}

                    s_node_id = cur_triplet.start_node.id
                    if ((s_node_id not in unique_node_ids) and (not self.db_conn.item_exist(s_node_id, id_type='node'))):
                        unique_node_ids.add(s_node_id)
                        creation_info[info_counter]['s_node'] = True
                    else:
                        existed_node_ids.add(s_node_id)

                    e_node_id = cur_triplet.end_node.id
                    if ((e_node_id not in unique_node_ids) and (not self.db_conn.item_exist(e_node_id, id_type='node'))):
                        unique_node_ids.add(e_node_id)
                        creation_info[info_counter]['e_node'] = True
                    else:
                        existed_node_ids.add(e_node_id)

                    unique_triplet_ids.add(cur_triplet.id)
                else:
                    existed_triplet_ids.add(cur_triplet.id)

            self.db_conn.create(triplets_to_create, creation_info)

        self.log(f"all/unique/existed triplets - {len(triplets)}/{len(unique_triplet_ids)}/{len(existed_triplet_ids)}", verbose=self.config.verbose)
        self.log(f"all/unique/existed/ nodes - {len(triplets)*2}/{len(unique_node_ids)}/{len(existed_node_ids)}", verbose=self.config.verbose)
        self.log("Triplets added successfully!", verbose=self.config.verbose)

    def delete_triplets(self, triplets: List[Triplet], batch_size: int = 64) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из модели.

        :param triplets: Набор триплетов для удаления из графового хранилища.
        :type triplets: List[Triplet]
        :param batch_size:  Количество триплетов, которое за одну delete-операцию удаляется из хранилища. Defaults to 64.
        :type batch_size: int, optional
        """
        steps = math.ceil(len(triplets) / batch_size)
        for step in tqdm(range(steps)):
            self.db_conn.delete(triplets[step*batch_size: (step+1)*batch_size])

@dataclass
class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента

    :param graph_struct: Знания, хранящиеся в графовой структуре данных.
    :type graph_struct: GraphModel
    :param graph_struct: Знания, хранящиеся в векторной структуре данных.
    :type graph_struct: EmbeddingsModel
    """
    graph_struct: GraphModel
    embeddings_struct: EmbeddingsModel
