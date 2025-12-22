from typing import List, Dict, Union
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Dataset, URIRef, Literal, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import requests
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
        self.create_namespace()

        query_endpoint = f"http://{self.config.host}:{self.config.port}/bigdata/namespace/{self.config.db_info['db']}/sparql"
        update_endpoint = query_endpoint

        self.namespace = Namespace(self.config.params['uri'])
        graph_name = f"http://{self.config.db_info['table']}.org"
        self.named_graph_uri = URIRef(graph_name)

        store = SPARQLUpdateStore(query_endpoint, update_endpoint)
        self.dataset = Dataset(store=store)
        self.graph = self.dataset.get_context(self.named_graph_uri)
        self.graph.open(query_endpoint)

        if self.config.need_to_clear:
            self.clear()

    def create_namespace(self):
        url = f'http://{self.config.host}:{self.config.port}/bigdata/namespace'
        formated_ns_config="".join(self.config.params['namespace_configuration'].format(namespace_name=self.config.db_info['db']).split("\n"))
        requests.post(url, data=formated_ns_config, headers={"Content-Type": "application/xml", 'Accept': 'application/xml'})

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
        if id_type is None:
            if detailed:
                result = {
                    'triplets': {'simple': 0, 'hyper': 0, 'episodic': 0, 'time': 0},
                    'nodes': {'object': 0, 'hyper': 0, 'episodic': 0, 'time': 0}
                }

                cnodes_query = f'PREFIX pai: {self.namespace} ASK WHERE {{ GRAPH {self.named_graph_uri} {{'
                n_output = self.execute_query(
                    "MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS nodeCount")
                r_output = self.execute_query(
                    "MATCH (a)-[rel]->(b) UNWIND type(rel) AS rel_type RETURN rel_type, count(rel) AS relCount")

                result['triplets'].update({item['rel_type']: int(item['relCount']) for item in r_output})
                result['nodes'].update({item['label']: int(item['nodeCount']) for item in n_output})

            else:
                n_output = self.execute_query(
                    "MATCH (a) RETURN count(a) as n_count")[0]
                r_output = self.execute_query(
                    "MATCH (a)-[rel]->(b) RETURN count(rel) as r_count")[0]
                result = {'triplets': r_output['r_count'],
                          'nodes': n_output['n_count']}

        elif id_type == 'node':
            n_output = self.execute_query(
                f'MATCH (a:{item_id.type.value}) WHERE a.str_id = "{item_id.id}" RETURN COUNT(a) as n_count')[0]
            result = n_output['n_count']

        elif id_type == 'relation':
            r_output = self.execute_query(
                f'MATCH (a)-[rel:{item_id.type.value}]->(b) WHERE rel.str_id = "{item_id.id}" RETURN COUNT(rel) as r_count')[0]
            result = r_output['r_count']

        elif id_type == 'triplet':
            r_output = self.execute_query(
                f'MATCH (a)-[rel]->(b) WHERE rel.t_id = "{item_id}" RETURN COUNT(rel) as r_count')[0]
            result = r_output['r_count']

        else:
            raise ValueError

        return result

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        if not isinstance(item_id, str):
            if type(item_id) in [NodeInfo, RelationInfo]:
                if not isinstance(item_id.id, str):
                    raise ValueError
            else:
                raise ValueError

        query = None
        prefix_query = f'PREFIX pai: {self.namespace} ASK WHERE {{ GRAPH {self.named_graph_uri} {{'

        if id_type == 'node':
            where_condition = f'pai:node pai:type pai:{item_id.type.value} ; pai:str_id "{item_id.id}" .'          
        elif id_type == 'relation':
            where_condition = f'pai:relation pai:type pai:{item_id.type.value} ; pai:str_id "{item_id.id}" .'  
        elif id_type == 'triplet':
            where_condition = f'pai:relation pai:t_id "{item_id}" .'
        else:
            raise ValueError
        
        query = f'{prefix_query} {where_condition} }} }}' 
        output = self.graph.query(query)
        formated_output = [row for row in output][0]

        return formated_output 

    def clear(self) -> None:
        sparql_query = f"CLEAR GRAPH {self.named_graph_uri}"
        self.graph.update(sparql_query)
