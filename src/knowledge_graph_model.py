from dataclasses import dataclass, field
from typing import List, Dict
import math
from tqdm import tqdm

from .db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriver, VectorDriverConfig, VectorDBInstance
from .db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from .db_drivers.graph_driver import GraphDriver, GraphDriverConfig, DEFAULT_NEO4J_CONFIG
from .utils.data_structs import Triplet, TripletCreator, NodeCreator, RelationCreator
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

    :param nodesdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений вершин из графовой модели. Значение по умолчанию NODES_DB_DEFAULT_DRIVER_CONFIG.
    :type nodesdb_driver_config: VectorDriverConfig
    :param tripletsdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений триплетов из графовой модели. Значение по умолчанию TRIPLETS_DB_DEFAULT_DRIVER_CONFIG.
    :type tripletsdb_driver_config: VectorDriverConfig
    :param tripletsdb_driver_config: Конфигурация класса, отвечающего за приведения текста в его векторрное представление с помощью embedder-модели. Значение по умолчанию EmbedderModelConfig().
    :type embedder_config: EmbedderModelConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(EMBEDDINGS_MODEL_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    nodesdb_driver_config: VectorDriverConfig = field(default_factory=lambda: NODES_DB_DEFAULT_DRIVER_CONFIG)
    tripletsdb_driver_config: VectorDriverConfig = field(default_factory=lambda: TRIPLETS_DB_DEFAULT_DRIVER_CONFIG)
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())
    log: Logger = field(default_factory=lambda: Logger(EMBEDDINGS_MODEL_LOG_PATH))
    verbose: bool = False

class EmbeddingsModel:
    """Модель хранения информации в векторной структуре данных.

    :param config: Конфигурация векторной модели данных. Значение по умолчанию EmbeddingsModelConfig().
    :type config: EmbeddingsModelConfig
    """
    def __init__(self, config: EmbeddingsModelConfig = EmbeddingsModelConfig()):
        self.config = config
        self.log = config.log
        self.vectordbs = {
            'nodes': VectorDriver.connect(config.nodesdb_driver_config),
            'triplets': VectorDriver.connect(config.tripletsdb_driver_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def create_triplets(self, triplets:List[Triplet], create_nodes:bool=True, batch_size:int=128, status_bar: bool = True)-> Dict[str, List[str]]:
        """Метод предназначен для добавления информации, представленной в виде списка триплетов, в векторную модель.
        Триплеты-дубликаты (по строковому представлению) в модель не добавляются.

        :param triplets: Набор триплетов для добавления в векторную модель данных.
        :type triplets: List[Triplet]
        :param create_nodes: Если True, то в векторную модель отдельно также будут добавлены вершины из триплетов. Вершины-дубликаты (по строковому представлению) не добавляются (отбрасываются), иначе False. Значение по умолчанию True.
        :type create_nodes: bool, optional
        :param batch_size: Количество триплетов, которое за одну create-операцию добавляются в векторную модель. Значение по умолчанию 128.
        :type batch_size: int, optional
        """
        self.log("Adding triples to vector-model...", verbose=self.config.verbose)
        unique_relation_ids, unique_node_ids = set(), set()
        existed_relation_ids, existed_node_ids = set(), set()

        batch_count = math.ceil(len(triplets) / batch_size)
        process = tqdm(range(batch_count)) if status_bar else range(batch_count)
        for batch_idx in process:
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
                    if ((cur_rel_id not in existed_relation_ids) and (not self.vectordbs['triplets'].item_exist(cur_rel_id))):
                        existed_relation_ids.add(cur_rel_id)
                        relation_ids.append(cur_triplet.relation.id)
                        relation_strs.append(triplet_str)

                if create_nodes:
                    self.log("\t- Also adding triplet-nodes in vector-model", verbose=self.config.verbose)
                    for node in [cur_triplet.start_node, cur_triplet.end_node]:
                        if node.id not in unique_node_ids:
                            unique_node_ids.add(node.id)
                            _, node_str = NodeCreator.stringify(node) if node.stringified is None else (None, node.stringified)
                            if ((node.id not in existed_node_ids) and (not self.vectordbs['nodes'].item_exist(node.id))):
                                existed_node_ids.add(node.id)
                                node_ids.append(node.id)
                                node_strs.append(node_str)

            self.create_stringified_triplets(relation_ids, relation_strs, node_ids, node_strs)

        self.log(f"all/unique/existed relations - {len(triplets)}/{len(unique_relation_ids)}/{len(existed_relation_ids)}", verbose=self.config.verbose)
        self.log(f"all/unique/existed nodes - {len(triplets)*2}/{len(unique_node_ids)}/{len(existed_node_ids)}", verbose=self.config.verbose)
        self.log("Triples were successfully added to vector-model!", verbose=self.config.verbose)
        return {'nodes': existed_node_ids, 'triplets': existed_relation_ids}

    def delete_triplets(self, triplets: List[Triplet], delete_nodes: bool = True) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из векторной модели.

        :param triplets: Набора триплетов для удаления.
        :type triplets: List[Triplet]
        :param delete_nodes: Если True, то из векторной модели также будут удалены вершины, которые принадлежат данным триплетам, иначе False, Значение по умолчанию True.
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
        :param nodes_ids: Идентификаторы вершин, с которыми они будут сохранены в моделе. Значение по умолчанию None.
        :type nodes_ids: List[str], optional
        :param stringified_nodes: Строковые представления вершин для сохранения в моделе. Значение по умолчанию None.
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
        :param nodes_ids: Идентификаторы вершин на удаление из модели. Значение по умолчанию None.
        :type nodes_ids: List[str], optional
        """
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)

    def create_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]) -> None:
        """Метод предназанчен для добавления набора объектов в одно из хранилищ данных векторной модели: для триплетов или вершин.

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
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(GRAPH_MODEL_LOG_PATH).
    :type log: Logger
    :param verbose: Если, True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    driver_config: GraphDriverConfig = field(default_factory=lambda: GRAPH_DB_DEFAULT_DRIVER_CONFIG)
    log: Logger = field(default_factory=lambda: Logger(GRAPH_MODEL_LOG_PATH))
    verbose: bool = False

class GraphModel:
    """Модель хранения информации в графовой структуре данных.

    :param config: Конфигурация графовой модели. Значение по умолчанию GraphModelConfig().
    :type config: GraphModelConfig
    """
    def __init__(self, config: GraphModelConfig = GraphModelConfig()) -> None:
        self.config = config
        self.log = config.log
        self.db_conn = GraphDriver.connect(self.config.driver_config)

    def create_triplets(self, triplets: List[Triplet], batch_size: int = 64, status_bar: bool = True) -> Dict[str, List[str]]:
        """Метод предназначен для сохранения информации, представленной в виде списка триплетов, в графовую модель.

        :param triplets: Набора триплетов для добавления в графовую модель.
        :type triplets: List[Triplet]
        :param batch_size: Количество триплетов, которое за одну create-операцию добавляется в модель. Значение по умолчанию 64.
        :type batch_size: int, optional
        """
        self.log("Adding triplets to graph-model...", verbose=self.config.verbose)
        unique_triplet_ids, unique_node_ids = set(), set()
        existed_triplet_ids, existed_node_ids = set(), set()
        created_triplet_ids, created_node_ids = set(), set()

        batches = math.ceil(len(triplets) / batch_size)
        process = tqdm(range(batches)) if status_bar else range(batches)
        for batch_idx in process:
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
                if cur_triplet.id in unique_triplet_ids:
                    continue
                else:
                    unique_triplet_ids.add(cur_triplet.id)

                if self.db_conn.item_exist(cur_triplet.id, id_type='triplet'):
                    existed_triplet_ids.add(cur_triplet.id)
                    continue
                else:
                    triplets_to_create.append(cur_triplet)
                    info_counter += 1
                    creation_info[info_counter] = {'s_node': False, 'e_node': False}
                    created_triplet_ids.add(cur_triplet.id)

                s_node_id = cur_triplet.start_node.id
                if (s_node_id not in unique_node_ids):
                    unique_node_ids.add(s_node_id)
                    if not self.db_conn.item_exist(s_node_id, id_type='node'):
                        creation_info[info_counter]['s_node'] = True
                        created_node_ids.add(s_node_id)
                    else:
                        existed_node_ids.add(s_node_id)

                e_node_id = cur_triplet.end_node.id
                if (e_node_id not in unique_node_ids):
                    unique_node_ids.add(e_node_id)
                    if not self.db_conn.item_exist(e_node_id, id_type='node'):
                        creation_info[info_counter]['e_node'] = True
                        created_node_ids.add(e_node_id)
                    else:
                        existed_node_ids.add(e_node_id)

            self.db_conn.create(triplets_to_create, creation_info)

        self.log(f"all/unique/existed triplets - {len(triplets)}/{len(unique_triplet_ids)}/{len(existed_triplet_ids)}", verbose=self.config.verbose)
        self.log(f"all/unique/existed nodes - {len(triplets)*2}/{len(unique_node_ids)}/{len(existed_node_ids)}", verbose=self.config.verbose)
        self.log("Triplets added successfully!", verbose=self.config.verbose)

        return {'triplets': created_triplet_ids, 'nodes': created_node_ids}

    def delete_triplets(self, triplets: List[Triplet], batch_size: int = 64) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из графовой модели.

        :param triplets: Набор триплетов для удаления из графовой модели.
        :type triplets: List[Triplet]
        :param batch_size:  Количество триплетов, которое за одну delete-операцию удаляется из графовой модели. Значение по умолчанию 64.
        :type batch_size: int, optional
        """
        steps = math.ceil(len(triplets) / batch_size)
        for step in tqdm(range(steps)):
            self.db_conn.delete(triplets[step*batch_size: (step+1)*batch_size])

class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента.

    :param graph_struct: Знания, хранящиеся в графовой структуре данных.
    :type graph_struct: GraphModel
    :param graph_struct: Знания, хранящиеся в векторной структуре данных.
    :type graph_struct: EmbeddingsModel
    """

    def __init__(self, graph_struct: GraphModel, embeddings_struct: EmbeddingsModel) -> None:
        self.graph_struct = graph_struct
        self.embeddings_struct = embeddings_struct

    def create_triplets_from_json(json_triplets: List[Dict]) -> List[Triplet]:
        """_summary_

        Триплет в json-формате должен иметь следующую структуру:
        - subject (Dict)
            - name (str)
            - type (str)
            - prop (Dict)
        - relation (Dict)
            - name (str)
            - type (str)
            - prop (Dict)
        - object (Dict)
            - name (str)
            - type (str)
            - prop (Dict)

        :param raw_json_triplets: _description_
        :type raw_json_triplets: List[Dict]
        :return: _description_
        :rtype: List[Triplet]
        """
        formated_triplets = []
        for raw_triplet in tqdm(json_triplets):
            subject = NodeCreator.create(raw_triplet['subject'])
            relation = RelationCreator.create(raw_triplet['relation'])
            object = NodeCreator.create(raw_triplet['object'])

            triplet = TripletCreator.create(start_node=subject, relation=relation, end_node=object)
            formated_triplets.append(triplet)
        return formated_triplets
