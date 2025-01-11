from dataclasses import dataclass, field
from typing import List, Dict, Union, Set
import math
from tqdm import tqdm

from ..db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriver, VectorDriverConfig, VectorDBInstance
from ..db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from ..utils.data_structs import Triplet, TripletCreator, NodeCreator, RelationCreator
from ..utils import Logger

NODES_DB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        path="../data/graph_structures/vectorized_nodes/default_densedb", db_info={'db': 'default_db', 'table': "vectorized_nodes"}))
TRIPLETS_DB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        path="../data/graph_structures/vectorized_triplets/default_densedb", db_info={'db': 'default_db', 'table': "vectorized_triplets"}))

EMBEDDINGS_MODEL_LOG_PATH = 'log/kg_model/embeddings'

@dataclass
class EmbeddingsModelConfig:
    """Конфигурация векторной модели данных.

    :param nodesdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений вершин из графовой модели. Значение по умолчанию NODES_DB_DEFAULT_DRIVER_CONFIG.
    :type nodesdb_driver_config: VectorDriverConfig
    :param tripletsdb_driver_config: Конфигурация векторной базы данных, которая будет отвечать за хранение векторных представлений триплетов из графовой модели. Значение по умолчанию TRIPLETS_DB_DEFAULT_DRIVER_CONFIG.
    :type tripletsdb_driver_config: VectorDriverConfig
    :param embedder_config: Конфигурация класса, отвечающего за приведения текста в его векторрное представление с помощью embedder-модели. Значение по умолчанию EmbedderModelConfig().
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

    def create_triplets(self, triplets:List[Triplet], create_nodes:bool=True, batch_size:int=128, status_bar: bool = True)-> Dict[str, Set[str]]:
        """Метод предназначен для добавления информации, представленной в виде списка триплетов, в векторную модель.
        Триплеты-дубликаты (по строковому представлению) в модель не добавляются.

        :param triplets: Набор триплетов для добавления в векторную модель данных.
        :type triplets: List[Triplet]
        :param create_nodes: Если True, то в векторную модель отдельно также будут добавлены вершины из триплетов. Вершины-дубликаты (по строковому представлению) не добавляются (отбрасываются), иначе False. Значение по умолчанию True.
        :type create_nodes: bool, optional
        :param batch_size: Количество триплетов, которое за одну create-операцию добавляются в векторную модель. Значение по умолчанию 128.
        :type batch_size: int, optional
        :param status_bar: Если True, то в stdout будет записываться прогресс операции (количество обработанных триплетов), иначе False. Значение по умолчанию True.
        :type status_bar: boll, optional
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

    def delete_triplets(self, triplets: List[Triplet], delete_info: Dict[int, Dict[str,bool]] = dict()) -> None:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из векторной модели.

        :param triplets: Набор триплетов на удаление.
        :type triplets: List[Triplet]
        :param delete__info: Информация для векторной структуры данных, чтобы удалить устаревшие вершины/триплеты и сохранить консистентность модели графа знаний.
        :type delete_nodes_info: Union[None, List[Dict[str,bool]]], optional
        """

        unique_nodes_ids, unique_relation_ids = set(), set()
        for i, triplet in enumerate(triplets):
            cur_info = delete_info.get(i, None)

            if (cur_info is None) or cur_info['triplet']:
                unique_relation_ids.add(triplet.relation.id)

            if (cur_info is None) or cur_info['s_node']:
                unique_nodes_ids.add(triplet.start_node.id)

            if (cur_info is None) or cur_info['e_node']:
                unique_nodes_ids.add(triplet.end_node.id)

        unique_nodes_ids = list(unique_nodes_ids) if len(unique_nodes_ids) > 0 else None
        unique_relation_ids = list(unique_relation_ids)

        self.delete_stringified_triplets(unique_relation_ids, unique_nodes_ids)

    def create_stringified_triplets(self, triplets_ids: List[str], stringified_triplets: List[str],
                     nodes_ids: List[str] = None, stringified_nodes: List[str] = None) -> None:
        """Метод предназначен для добавления строковых представлений триплетов/вершин в векторную модель.

        :param triplets_ids: Идентификаторы триплетов, с которыми они будут сохранены в модель.
        :type triplets_ids: List[str]
        :param stringified_triplets: Строковые представления триплетов для сохранения в модель.
        :type stringified_triplets: List[str]
        :param nodes_ids: Идентификаторы вершин, с которыми они будут сохранены в модель. Значение по умолчанию None.
        :type nodes_ids: List[str], optional
        :param stringified_nodes: Строковые представления вершин для сохранения в модель. Значение по умолчанию None.
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

    def count_items(self) -> Dict[str, int]:
        nodes_count = self.vectordbs['nodes'].count_items()
        triplets_count = self.vectordbs['triplets'].count_items()
        return {'nodes': nodes_count, 'triplets': triplets_count}

    def clear(self) -> None:
        """Метод предназначен для удаления содержимого векторной модели данных.
        """
        self.vectordbs['nodes'].clear()
        self.vectordbs['triplets'].clear()
