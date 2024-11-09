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
        path="../data/graph_structures/vectorized_nodes/v8/densedb", db_name="vectorized_nodes"))
TRIPLETS_DB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        path="../data/graph_structures/vectorized_triplets/v4/densedb", db_name="vectorized_triplets"))

EMBEDDINGS_MODEL_LOG_PATH = 'log/em'

@dataclass
class EmbeddingsModelConfig:
    """_summary_
    """
    #
    nodesdb_driver_config: VectorDriverConfig = field(default_factory=lambda: NODES_DB_DEFAULT_DRIVER_CONFIG)
    tripletsdb_driver_config: VectorDriverConfig = field(default_factory=lambda: TRIPLETS_DB_DEFAULT_DRIVER_CONFIG)
    #
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())
    #
    log: Logger = field(default_factory=lambda: Logger(EMBEDDINGS_MODEL_LOG_PATH))
    verbose: bool = False

class EmbeddingsModel:
    def __init__(self, config: EmbeddingsModelConfig = EmbeddingsModelConfig()):
        self.config = config
        self.log = config.log
        self.vectordbs = {
            'nodes': VectorDriver.connect(config.nodesdb_driver_config),
            'triplets': VectorDriver.connect(config.tripletsdb_driver_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def create_triplets(self, triplets:List[Triplet], add_nodes:bool=True, batch_size:int=128)-> None:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        :param add_nodes: _description_, defaults to True
        :type add_nodes: bool, optional
        :param batch_size: _description_, defaults to 128
        :type batch_size: int, optional
        """
        self.log("Adding triples to vector-model...", verbose=self.config.verbose)
        unique_nodes_ids, unique_triplets_ids = set(), set()

        batch_count = math.ceil(len(triplets) / batch_size)
        for batch_idx in tqdm(range(batch_count)):
            triplets_ids, triplets_strs = list(), list()
            nodes_ids, nodes_strs = list(), list()

            for triplet_idx in range(batch_idx*batch_size, (batch_idx+1)*batch_size):
                if triplet_idx >= len(triplets):
                    break

                triplet = triplets[triplet_idx]
                _, triplet_str =  TripletCreator.stringify(triplet) if triplet.stringified is None else (triplet.id, triplet.stringified)
                if triplet.id not in unique_triplets_ids:
                    unique_triplets_ids.add(triplet.id)
                    triplets_ids.append(triplet.id)
                    triplets_strs.append(triplet_str)

                if add_nodes:
                    self.log("\t- Also adding triplet-nodes in vector-model", verbose=self.config.verbose)
                    for node in [triplet.start_node, triplet.end_node]:
                        if node.id not in unique_nodes_ids:
                            _, node_str = NodeCreator.stringify(node) if node.stringified is None else (node.id, node.stringified)
                            unique_nodes_ids.add(node.id)
                            nodes_ids.append(node.id)
                            nodes_strs.append(node_str)

            self.create_stringified_triplets(triplets_ids, triplets_strs, nodes_ids, nodes_strs)

        self.log(f"all/unique_triplets - {len(triplets)}/{len(unique_triplets_ids)}", verbose=self.config.verbose)
        self.log(f"all/unique_nodes - {len(triplets)*2}/{len(unique_nodes_ids)}", verbose=self.config.verbose)
        self.log("Triples were successfully added to vector-model!", verbose=self.config.verbose)

    def delete_triplets(self, triplets: List[Triplet], delete_nodes: bool = True) -> None:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        :param delete_nods: _description_, defaults to True
        :type delete_nods: bool, optional
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
        """_summary_

        :param triplets_ids: _description_
        :type triplets_ids: List[str]
        :param stringified_triplets: _description_
        :type stringified_triplets: List[str]
        :param nodes_ids: _description_, defaults to None
        :type nodes_ids: List[str], optional
        :param stringified_nodes: _description_, defaults to None
        :type stringified_nodes: List[str], optional
        """
        if len(triplets_ids):
            self.create_instances('triplets', triplets_ids, stringified_triplets)
        if nodes_ids is not None and len(nodes_ids):
            self.create_instances('nodes', nodes_ids, stringified_nodes)

    def delete_stringified_triplets(self, triplets_ids: List[str], nodes_ids: List[str] = None) -> None:
        """_summary_

        :param triplets_ids: _description_
        :type triplets_ids: List[str]
        :param nodes_ids: _description_, defaults to None
        :type nodes_ids: List[str], optional
        """
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)

    def create_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]) -> None:
        """_summary_

        :param db_type: _description_
        :type db_type: str
        :param ids: _description_
        :type ids: List[str]
        :param stringified_instances: _description_
        :type stringified_instances: List[str]
        """
        embs = self.embedder.encode_passages(stringified_instances)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb, metadata={'id': id})
                            for id, doc, emb in zip(ids, stringified_instances, embs)]
        self.vectordbs[db_type].create(formated_instances)

    def delete_instances(self, db_type: str, ids: List[str]) -> None:
        """_summary_

        :param db_type: _description_
        :type db_type: str
        :param ids: _description_
        :type ids: List[str]
        """
        self.vectordbs[db_type].delete(ids)

    def read_embbeddings(self, db_type: str, ids: List[str]) -> List[List[float]]:
        """_summary_

        :param db_type: _description_
        :type db_type: str
        :param ids: _description_
        :type ids: List[str]
        :return: _description_
        :rtype: List[List[float]]
        """
        instances = self.vectordbs[db_type].read(ids, includes=['embeddings'])
        embeddings = list(map(lambda inst: inst.embedding, instances))
        return embeddings

GRAPH_DB_DEFAULT_DRIVER_CONFIG = GraphDriverConfig(db_vendor='neo4j', db_config=DEFAULT_NEO4J_CONFIG)
GRAPH_MODEL_LOG_PATH = 'log/gm'

@dataclass
class GraphModelConfig:
    #
    driver_config: GraphDriverConfig = field(default_factory=lambda: GRAPH_DB_DEFAULT_DRIVER_CONFIG)
    #
    log: Logger = field(default_factory=lambda: Logger(GRAPH_MODEL_LOG_PATH))
    verbose: bool = False

class GraphModel:
    def __init__(self, config: GraphModelConfig = GraphModelConfig()) -> None:
        self.config = config
        self.log = config.log
        self.db_conn = GraphDriver.connect(self.config.driver_config)

    def create_triplets(self, triplets: List[Triplet], batch_size: int = 64) -> None:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        """
        self.log("Adding triplets to graph-model...", verbose=self.config.verbose)


        steps = math.ceil(len(triplets) / batch_size)
        for step in tqdm(range(steps)):
            # проверка триплетов на наличие дубликатов
            # метода create есть дополнительный аргумент

            created_nodes, created_rels = self.db_conn.create(triplets[step*batch_size: (step+1)*batch_size])
            created_nodes_count += created_nodes
            created_rels_count += created_rels

        self.log(f"all/created_relations - {len(triplets)}/{created_rels_count}", verbose=self.config.verbose)
        self.log(f"all/created_nodes - {len(triplets)*2}/{created_nodes_count}", verbose=self.config.verbose)
        self.log("Triplets added successfully!", verbose=self.config.verbose)

    def delete_triplets(self, triplets: List[Triplet], batch_size: int = 64) -> None:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        """
        steps = math.ceil(len(triplets) / batch_size)
        for step in tqdm(range(steps)):
            self.db_conn.delete(triplets[step*batch_size: (step+1)*batch_size])

@dataclass
class KnowledgeGraphModel:
    graph_struct: GraphModel
    embeddings_struct: EmbeddingsModel
