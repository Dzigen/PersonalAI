from typing import List, Dict, Union
#from SPARQLWrapper import SPARQLWrapper, JSON
#from rdflib import Dataset, URIRef, Literal, Namespace
#from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import json
import os

from .configs import DEFAULT_BLAZEGRAPH_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.errors import ReturnInfo
from ....utils.data_structs import Node, NODES_TYPES_MAP, TripletCreator, Relation, RELATIONS_TYPES_MAP, \
    RelationType, NodeInfo, RelationInfo, from_str_to_nodeinfo, from_str_to_relationinfo
from ....utils import Triplet, NodeType


class BlazeGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_BLAZEGRAPH_CONFIG) -> None:
        if isinstance(config, dict):
            config = GraphDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: GraphDBConnectionConfig = config

    def open_connection(self) -> None:
        query_endpoint = f"http://{self.config.host}:{self.config.port}/bigdata/namespace/kb/sparql"
        update_endpoint = query_endpoint

        graph_name = f"{self.config.db_info['db']}{self.config.db_info['table']}"

        self.namespace = Namespace(f"{self.config.params['namespace']}")
        self.named_graph_uri = URIRef(f"{self.config.params['namespace']}/{graph_name}")

        store = SPARQLUpdateStore(query_endpoint, update_endpoint)
        g = Dataset(store=store)
        self.graph = g.get_context(self.named_graph_uri)
        self.graph.open(query_endpoint)
        self.graph.bind('pai', self.namespace)

        if self.config.need_to_clear:
            self.clear()

    def close_connection(self) -> None:
        try:
            self.graph.close()
        except (AttributeError, TypeError):
            pass

    def __del__(self):
        self.close_connection()

    def is_open(self) -> bool:
        # TODO
        raise NotImplementedError

    def create_node_query(self, node: Node) -> str:
        # TODO
        raise NotImplementedError

    def create_rel_query(self, triplet: Triplet) -> str:
        # TODO
        raise NotImplementedError

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> ReturnInfo:
        # TODO
        raise NotImplementedError

    def read(self, ids: List[str]) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def update(self, items: List[Triplet]) -> ReturnInfo:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # TODO
        raise NotImplementedError

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        # TODO
        raise NotImplementedError

    def parse_query_nodes_output(self, output: object) -> List[Node]:
        # TODO
        raise NotImplementedError

    def parse_query_triplets_output(self, output: object) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def get_adjecent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        # TODO
        raise NotImplementedError

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        # TODO
        raise NotImplementedError

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        # TODO
        raise NotImplementedError

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        # TODO
        raise NotImplementedError

    def clear(self) -> None:
        sparql_query = "DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }"
        self.graph.update(sparql_query)
