from typing import List, Dict, Union, Tuple
from SPARQLWrapper import SPARQLWrapper, POST
from rdflib import Dataset, URIRef, Literal, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import requests
import json
import os

from .configs import DEFAULT_BLAZEGRAPH_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ...utils import restore_connection, retry
from ....utils.data_structs import Triplet, Node, TripletCreator, NodeCreator, \
    NodeType, RelationCreator, RelationType, NODES_TYPES_MAP, RELATIONS_TYPES_MAP, \
    NodeInfo, RelationInfo, create_id, TripletInfo


# Useful Material: "Графы знаний | Лекция 3 - SPARQL, Графовые хранилища"
# https://www.youtube.com/watch?v=z7coG_7kzM8&list=LL&index=5


class BlazeGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_BLAZEGRAPH_CONFIG) -> None:
        if isinstance(config, dict):
            config = GraphDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: GraphDBConnectionConfig = config

        # initing uri`s
        base_uriprefix = self.config.params['uri_prefix']

        self.custom_uries = {
            'node': Namespace(base_uriprefix + '/node/internal_id#'),
            'relation': Namespace(base_uriprefix + '/relation/internal_id#'),
        }

        self.general_uries = {
            'element': {
                'prefix': Namespace(base_uriprefix + '/element#'),

                'node': 'node',
                'relation': 'relation'
            },

            'node': {
                'field_prefix': Namespace(base_uriprefix + '/node/field#'),

                'type': {
                    'prefix': Namespace(base_uriprefix + '/node/type#'),

                    'episodic': 'episodic',
                    'hyper': 'thesis',
                    'object': 'object',
                    'time': 'time'
                }
            },

            'relation': {
                'field_prefix': Namespace(base_uriprefix + '/relation/field#'),

                't_id': 't_id',

                'type': {
                    'prefix': Namespace(base_uriprefix + '/relation/type#'),

                    'episodic': 'episodic',
                    'hyper': 'hyper',
                    'simple': 'simple',
                    'time': 'time'
                }
            },

            'general_fields': {
                'prefix': Namespace(base_uriprefix + '/general_field#'),

                'type': 'type',
                'element': 'element',
                'str_id': 'str_id',
                'name': 'name',
                'properties': 'properties'
            }
        }

    @retry
    def open_connection(self) -> None:
        self.create_namespace()

        query_endpoint = f"http://{self.config.host}:{self.config.port}/bigdata/namespace/{self.config.db_info['db']}/sparql"
        update_endpoint = query_endpoint

        graph_name = f"http://{self.config.db_info['table']}.org"
        self.named_graph_uri = URIRef(graph_name)

        store = SPARQLUpdateStore(query_endpoint, update_endpoint)
        self.dataset = Dataset(store=store)
        self.graph = self.dataset.get_context(self.named_graph_uri)
        self.graph.open(query_endpoint)

        self.update_endpoint = SPARQLWrapper(update_endpoint)

        if self.config.need_to_clear:
            self.clear()

    @retry
    def create_namespace(self):
        url = f'http://{self.config.host}:{self.config.port}/bigdata/namespace'
        formated_ns_config = "".join(self.config.params['namespace_configuration'].format(namespace_name=self.config.db_info['db']).split("\n"))
        requests.post(url, data=formated_ns_config, headers={"Content-Type": "application/xml", 'Accept': 'application/xml'})

    @retry
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

    @restore_connection
    def execute(self, query: str, mode: str = 'read') -> object:
        output = None
        if mode == 'read':
            output = self.graph.query(query)
        elif mode == 'write':
            self.update_endpoint.setQuery(query)
            self.update_endpoint.setMethod(POST)
            output = self.update_endpoint.query()
        else:
            raise ValueError
        return output

    def create_node_query(self, node: Node) -> Tuple[str, str]:
        insert_node_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX node: <{node_uriprefix}>
        PREFIX node_type: <{nodetype_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        INSERT DATA {{
            GRAPH <{named_graph_uri}> {{
                node:{internal_id} general_predicate:element element:{spec_element} ;
                general_predicate:type node_type:{type} ;
                general_predicate:str_id "{str_id}" ;
                general_predicate:name {name} ;
                general_predicate:properties '{properties_dump}' .
            }}
        }}
        '''

        node_iid = create_id()
        properties_dump = json.dumps(node.prop, ensure_ascii=False)

        formated_query = insert_node_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            node_uriprefix=self.custom_uries['node'],
            nodetype_uriprefix=self.general_uries['node']['type']['prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            internal_id=node_iid,
            spec_element=self.general_uries['element']['node'],
            type=node.type.value,
            str_id=node.id,
            name=json.dumps(node.name, ensure_ascii=False),
            properties_dump=properties_dump
        )

        return formated_query, node_iid

    def create_rel_query(self, triplet: Triplet) -> Tuple[str, str]:
        insert_relation_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation: <{relation_uriprefix}>
        PREFIX relation_type: <{relationtype_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        INSERT {{
            GRAPH <{named_graph_uri}> {{
                ?s relation:{rel_iid} ?o.
                relation:{rel_iid} general_predicate:element element:relation ;
                                general_predicate:type relation_type:{type} ;
                                relation_predicate:t_id "{t_id}" ;
                                general_predicate:str_id "{str_id}" ;
                                general_predicate:name {name} ;
                                general_predicate:properties '{properties_dump}' .
            }}
        }}
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                ?s general_predicate:element element:node ;
                    general_predicate:str_id "{snode_strid}" .
                ?o general_predicate:element element:node ;
                    general_predicate:str_id "{enode_strid}" .
            }}
        }}
        '''

        rel_iid = create_id()
        properties_dump = json.dumps(triplet.relation.prop, ensure_ascii=False)

        formated_query = insert_relation_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relation_uriprefix=self.custom_uries['relation'],
            relationtype_uriprefix=self.general_uries['relation']['type']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            snode_strid=triplet.start_node.id,
            enode_strid=triplet.end_node.id,
            rel_iid=rel_iid,
            type=triplet.relation.type.value,
            t_id=triplet.id,
            str_id=triplet.relation.id,
            name=json.dumps(triplet.relation.name, ensure_ascii=False),
            properties_dump=properties_dump
        )

        return formated_query, rel_iid

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if not isinstance(triplet.id, str):
                raise ValueError(f"* triplets: {triplets}\n* creation_info: {creation_info}")
        unique_ids = set(map(lambda triplet: triplet.id, triplets))
        if len(triplets) != len(unique_ids):
            raise ValueError(f"* triplets: {triplets}")

        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)
            if cur_info is None or cur_info['s_node']:
                insert_subj_query, _ = self.create_node_query(triplet.start_node)
                # print(insert_subj_query)
                self.execute(insert_subj_query, 'write')
            if cur_info is None or cur_info['e_node']:
                insert_obj_query, _ = self.create_node_query(triplet.end_node)
                # print(insert_obj_query)
                self.execute(insert_obj_query, 'write')

            insert_rel_query, _ = self.create_rel_query(triplet)
            # print(insert_rel_query)
            self.execute(insert_rel_query, 'write')

    def read(self, ids: List[str]) -> List[Triplet]:
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError(f"* bad id: {t_id}\n* ids: {ids}")

        select_triples_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT ?snode_uri ?snode_strid ?snode_type ?snode_name ?snode_properties ?rel_uri ?rel_tid ?rel_strid ?rel_type ?rel_name ?rel_properties ?enode_uri ?enode_strid ?enode_type ?enode_name ?enode_properties
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                ?snode_uri ?rel_uri ?enode_uri .
                ?rel_uri general_predicate:element element:relation ;
                        relation_predicate:t_id ?rel_tid ;
                        general_predicate:str_id ?rel_strid ;
                        general_predicate:type ?rel_type ;
                        general_predicate:name ?rel_name ;
                        general_predicate:properties ?rel_properties .
                ?snode_uri general_predicate:element element:node ;
                        general_predicate:str_id ?snode_strid ;
                        general_predicate:type ?snode_type ;
                        general_predicate:name ?snode_name ;
                        general_predicate:properties ?snode_properties .
                ?enode_uri general_predicate:element element:node ;
                        general_predicate:str_id ?enode_strid ;
                        general_predicate:type ?enode_type ;
                        general_predicate:name ?enode_name ;
                        general_predicate:properties ?enode_properties .
                FILTER (?rel_tid IN ({tids_list}))
            }}
        }}
        '''

        t_ids = ', '.join(list(map(lambda id: f'"{id}"', ids)))
        formated_query = select_triples_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            tids_list=t_ids)
        # print(formated_query)
        raw_output = self.execute(formated_query)
        triplets = self.parse_query_triplets_output(raw_output)
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError(f"* bad id: {t_id}\n* ids: {ids}")

        #
        select_triplesuri_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT ?rel_tid ?snode_uri ?rel_uri ?enode_uri
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                ?snode_uri ?rel_uri ?enode_uri .
                ?rel_uri general_predicate:element element:relation ;
                        relation_predicate:t_id ?rel_tid FILTER (?rel_tid IN ({tids_list})).
                ?snode_uri general_predicate:element element:node .
                ?enode_uri general_predicate:element element:node .
            }}
        }}
        '''
        t_ids = ', '.join(list(map(lambda id: f'"{id}"', ids)))
        formated_query = select_triplesuri_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            tids_list=t_ids
        )
        # print(formated_query)
        raw_output = self.execute(formated_query)
        formated_triplesuri = dict()
        for row in raw_output:
            formated_triplesuri[str(row['rel_tid'])] = {
                's_node': f"<{row['snode_uri']}>",
                'rel': f"<{row['rel_uri']}>",
                'e_node': f"<{row['enode_uri']}>"
            }
        # print(formated_triplesuri)

        delete_object_query = '''
        DELETE {{
            GRAPH <{named_graph_uri}> {{
                ?object_uri ?field ?value .
            }}
        }}
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                ?object_uri ?field ?value .
                FILTER(?object_uri IN ({uries_list}))
            }}
        }}
        '''

        reluries_list = ', '.join([info['rel'] for info in formated_triplesuri.values()])
        formated_query = delete_object_query.format(
            named_graph_uri=self.named_graph_uri, uries_list=reluries_list)
        # print(formated_query)
        self.execute(formated_query, 'write')

        nodeuries_list = []
        for i, t_id in enumerate(ids):
            cur_info = delete_info.get(i, None)
            for node_pos in ['s_node', 'e_node']:
                if cur_info is None or cur_info[node_pos]:
                    if t_id in formated_triplesuri:
                        nodeuries_list.append(formated_triplesuri[t_id][node_pos])
        nodeuries_list = ', '.join(nodeuries_list)
        formated_query = delete_object_query.format(
            named_graph_uri=self.named_graph_uri, uries_list=nodeuries_list)
        # print(formated_query)
        self.execute(formated_query, "write")

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        if type(object_type) not in [RelationType, NodeType]:
            raise ValueError(f"object_type: {object_type}")

        if not isinstance(name, str):
            raise ValueError(f"name: {name}")

        if len(name) < 1:
            raise ValueError(f"name: {name}")

        dump_name = json.dumps(name, ensure_ascii=False)
        if object == 'relation':
            select_triples_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX relation_predicate: <{relationpredicate_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            SELECT ?snode_uri ?snode_strid ?snode_type ?snode_name ?snode_properties ?rel_uri ?rel_tid ?rel_strid ?rel_type ?rel_name ?rel_properties ?enode_uri ?enode_strid ?enode_type ?enode_name ?enode_properties
            FROM NAMED <{named_graph_uri}>
            WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?snode_uri ?rel_uri ?enode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    FILTER (?rel_name = {rel_name} && ?rel_type = {rel_type})
                }}
            }}
            '''
            formated_query = select_triples_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                rel_name=dump_name,
                rel_type=f"<{self.general_uries['relation']['type']['prefix']}{object_type.value}>")
            # print(formated_query)
            raw_output = self.execute(formated_query)
            formated_output = self.parse_query_triplets_output(raw_output)

        elif object == 'node':
            select_nodes_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            SELECT ?node_uri ?str_id ?type ?name ?properties
            FROM NAMED <{named_graph_uri}>
            WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?node_uri general_predicate:element element:node ;
                            general_predicate:str_id ?str_id ;
                            general_predicate:type ?type ;
                            general_predicate:name ?name ;
                            general_predicate:properties ?properties .
                    FILTER (?name  = {name} && ?type = {type})
                }}
            }}
            '''
            formated_query = select_nodes_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                name=dump_name, type=f"<{self.general_uries['node']['type']['prefix']}{object_type.value}>"
            )
            # print(formated_query)
            raw_output = self.execute(formated_query)
            formated_output = self.parse_query_nodes_output(raw_output)

        else:
            raise ValueError(f"object: {object}")

        return formated_output

    def parse_query_nodes_output(self, output: object) -> List[Node]:
        formated_nodes = []
        for raw_node in output:
            node_type = NODES_TYPES_MAP[raw_node['type'].split("#")[1]]
            node_props = json.loads(raw_node['properties'])
            node = NodeCreator.create(
                n_type=node_type, name=str(raw_node['name']),
                prop=node_props, add_stringified_node=False)

            formated_nodes.append(node)
        return formated_nodes

    def parse_query_triplets_output(self, output: object) -> List[Triplet]:
        formated_triplets: List[Triplet] = []
        for raw_triplet in output:

            snode_type = NODES_TYPES_MAP[raw_triplet['snode_type'].split("#")[1]]
            snode_props = json.loads(raw_triplet['snode_properties'])
            snode = NodeCreator.create(
                n_type=snode_type, name=str(raw_triplet['snode_name']),
                prop=snode_props, add_stringified_node=False)

            enode_type = NODES_TYPES_MAP[raw_triplet['enode_type'].split("#")[1]]
            enode_props = json.loads(raw_triplet['enode_properties'])
            enode = NodeCreator.create(
                n_type=enode_type, name=str(raw_triplet['enode_name']),
                prop=enode_props, add_stringified_node=False)

            rel_type = RELATIONS_TYPES_MAP[raw_triplet['rel_type'].split("#")[1]]
            rel_props = json.loads(raw_triplet['rel_properties'])
            relation = RelationCreator.create(
                r_type=rel_type, name=str(raw_triplet['rel_name']),
                prop=rel_props)

            triplet = TripletCreator.create(
                snode, relation, enode,
                add_stringified_triplet=True, t_id=str(raw_triplet['rel_tid'])
            )
            formated_triplets.append(triplet)

        return formated_triplets

    def get_adjacent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time]) -> List[NodeInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        select_adjnodes_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT ?node_strid ?node_type
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                {{
                    ?root_node ?p ?o .
                    ?root_node general_predicate:element element:node ;
                            general_predicate:type {root_type} ;
                            general_predicate:str_id "{root_strid}" .
                    ?p general_predicate:element element:relation .
                    ?o general_predicate:element element:node ;
                            general_predicate:type ?node_type ;
                            general_predicate:str_id ?node_strid .
                    FILTER(?node_type IN ({types_list}))
                }}
                UNION
                {{
                    ?s ?p ?root_node .
                    ?root_node general_predicate:element element:node ;
                            general_predicate:type {root_type} ;
                            general_predicate:str_id "{root_strid}" .
                    ?p general_predicate:element element:relation .
                    ?s general_predicate:element element:node ;
                        general_predicate:type ?node_type ;
                        general_predicate:str_id ?node_strid .
                    FILTER(?node_type IN ({types_list}))
                }}
            }}
        }}
        '''
        accepted_tnodes = ', '.join(list(map(lambda tpe: f"<{self.general_uries['node']['type']['prefix']}{tpe.value}>", accepted_n_types)))
        formated_query = select_adjnodes_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            root_type=f"<{self.general_uries['node']['type']['prefix']}{base_node.type.value}>",
            root_strid=base_node.id,
            types_list=accepted_tnodes
        )
        # print(formated_query)
        raw_output = self.execute(formated_query)
        formated_nodes = [NodeInfo(id=str(node['node_strid']), type=NODES_TYPES_MAP[node['node_type'].split("#")[1]]) for node in raw_output]
        return formated_nodes

    def get_incident_triples(self, base_node: NodeInfo,
                             accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time],
                             accepted_r_types: Union[List[RelationType], None] = None) \
            -> List[TripletInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        if accepted_r_types is None:
            accepted_r_types = [RelationType.simple, RelationType.hyper, RelationType.episodic, RelationType.time]

        select_inctriples_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT DISTINCT ?snode_strid ?snode_type ?rel_tid ?rel_strid ?rel_type ?enode_strid ?enode_type
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                {{
                    ?root_node ?p ?o .
                    ?p general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type .
                    ?root_node general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type .
                    ?o general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type .
                    FILTER(?snode_strid = "{root_strid}" && ?snode_type = {root_type} && ?enode_type IN ({ntypes_list}) && ?rel_type IN ({rtypes_list}))
                }}
                UNION
                {{
                    ?s ?p ?root_node .
                    ?p general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type .
                    ?s general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type .
                    ?root_node general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type .
                    FILTER(?enode_strid = "{root_strid}" && ?enode_type = {root_type} && ?snode_type IN ({ntypes_list}) && ?rel_type IN ({rtypes_list}))
                }}
            }}
        }}
        '''
        accepted_tnodes = ', '.join(list(map(lambda tpe: f"<{self.general_uries['node']['type']['prefix']}{tpe.value}>", accepted_n_types)))
        accepted_trelations = ', '.join(list(map(lambda tpe: f"<{self.general_uries['relation']['type']['prefix']}{tpe.value}>", accepted_r_types)))

        formated_query = select_inctriples_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            root_type=f"<{self.general_uries['node']['type']['prefix']}{base_node.type.value}>",
            root_strid=base_node.id,
            ntypes_list=accepted_tnodes,
            rtypes_list=accepted_trelations,
        )
        output = self.execute(formated_query)

        triples_info = []
        for triple in output:
            snode_info = NodeInfo(id=str(triple['snode_strid']), type=NODES_TYPES_MAP[triple['snode_type'].split("#")[1]])
            enode_info = NodeInfo(id=str(triple['enode_strid']), type=NODES_TYPES_MAP[triple['enode_type'].split("#")[1]])
            rel_info = RelationInfo(id=str(triple['rel_strid']), type=RELATIONS_TYPES_MAP[triple['rel_type'].split("#")[1]])
            triples_info.append(TripletInfo(id=str(triple['rel_tid']), start_node=snode_info, relation=rel_info, end_node=enode_info))

        return triples_info

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")
        if not isinstance(id_type, str):
            raise ValueError(f"id_type: {id_type}")

        if id_type == 'triplet':
            select_statement = '(?rel_tid AS ?t_id)'
        elif id_type == 'relation':
            select_statement = '(?rel_strid as ?r_id)'
        elif id_type == 'both':
            select_statement = '(?rel_tid AS ?t_id) (?rel_strid AS ?r_id)'
        else:
            raise ValueError(f"id_type: {id_type}")

        select_relationids_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT DISTINCT {select_statement}
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                {{
                    ?snode_uri ?rel_uri ?enode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    FILTER(?snode_strid = "{snode_strid}" && ?snode_type = {snode_type} && ?enode_strid = "{enode_strid}" && ?enode_type = {enode_type})
                }}
                UNION
                {{
                    ?enode_uri ?rel_uri ?snode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    FILTER(?snode_strid = "{snode_strid}" && ?snode_type = {snode_type} && ?enode_strid = "{enode_strid}" && ?enode_type = {enode_type})
                }}
            }}
        }}
        '''
        formated_query = select_relationids_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            select_statement=select_statement,
            named_graph_uri=self.named_graph_uri,
            snode_strid=node1.id, snode_type=f"<{self.general_uries['node']['type']['prefix']}{node1.type.value}>",
            enode_strid=node2.id, enode_type=f"<{self.general_uries['node']['type']['prefix']}{node2.type.value}>"
        )
        # print(formated_query)
        raw_output = self.execute(formated_query)

        formated_info = []
        for raw_rel in raw_output:
            tmp_info = dict()
            if id_type in ['both', 'triplet']:
                tmp_info['t_id'] = str(raw_rel['t_id'])

            if id_type in ['both', 'relation']:
                tmp_info['r_id'] = str(raw_rel['r_id'])

            formated_info.append(tmp_info)

        return formated_info

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        formated_triplets = []
        select_triples_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT ?snode_uri ?snode_strid ?snode_type ?snode_name ?snode_properties ?rel_uri ?rel_tid ?rel_strid ?rel_type ?rel_name ?rel_properties ?enode_uri ?enode_strid ?enode_type ?enode_name ?enode_properties
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                {{
                    ?snode_uri ?rel_uri ?enode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    {filter_operator}
                }}
                UNION
                {{
                    ?enode_uri ?rel_uri ?snode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    {filter_operator}
                }}
            }}
        }}
        '''
        if subj_names:
            for subj_name in subj_names:
                subj_dump = json.dumps(subj_name.lower(), ensure_ascii=False)
                snodetype_uri = f"<{self.general_uries['node']['type']['prefix']}object>"
                enodetype_uri = f"<{self.general_uries['node']['type']['prefix']}{obj_type}>"
                filter_operator = f"FILTER(?snode_type = {snodetype_uri} && ?enode_type = {enodetype_uri} && LCASE(str(?snode_name) = {subj_dump})"
                formated_query = select_triples_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                    named_graph_uri=self.named_graph_uri, filter_operator=filter_operator
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                formated_triplets += self.parse_query_triplets_output(raw_output)
        elif obj_names:
            for obj_name in obj_names:
                obj_dump = json.dumps(obj_name.lower(), ensure_ascii=False)
                snodetype_uri = f"<{self.general_uries['node']['type']['prefix']}object>"
                enodetype_uri = f"<{self.general_uries['node']['type']['prefix']}{obj_type}>"
                filter_operator = f"FILTER(?snode_type = {snodetype_uri} && ?enode_type = {enodetype_uri} && LCASE(str(?enode_name) = {obj_dump})"
                formated_query = select_triples_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                    named_graph_uri=self.named_graph_uri, filter_operator=filter_operator
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                formated_triplets += self.parse_query_triplets_output(raw_output)
        else:
            snodetype_uri = f"<{self.general_uries['node']['type']['prefix']}object>"
            enodetype_uri = f"<{self.general_uries['node']['type']['prefix']}{obj_type}>"
            filter_operator = f"FILTER(?snode_type = {snodetype_uri} && ?enode_type = {enodetype_uri})"
            formated_query = select_triples_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                named_graph_uri=self.named_graph_uri, filter_operator=filter_operator
            )
            # print(formated_query)
            raw_output = self.execute(formated_query)
            formated_triplets += self.parse_query_triplets_output(raw_output)

        return formated_triplets

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")
        if (not self.item_exist(node1, 'node')) or (not self.item_exist(node2, 'node')):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")

        select_triplet_query = '''
        PREFIX element: <{element_uriprefix}>
        PREFIX relation_predicate: <{relationpredicate_uriprefix}>
        PREFIX general_predicate: <{generalpredicate_uriprefix}>
        SELECT DISTINCT ?snode_uri ?snode_strid ?snode_type ?snode_name ?snode_properties ?rel_uri ?rel_tid ?rel_strid ?rel_type ?rel_name ?rel_properties ?enode_uri ?enode_strid ?enode_type ?enode_name ?enode_properties
        FROM NAMED <{named_graph_uri}>
        WHERE {{
            GRAPH <{named_graph_uri}> {{
                {{
                    ?snode_uri ?rel_uri ?enode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    FILTER(?snode_strid = "{snode_strid}" && ?snode_type = {snode_type} && ?enode_strid = "{enode_strid}" && ?enode_type = {enode_type})
                }}
                UNION
                {{
                    ?enode_uri ?rel_uri ?snode_uri .
                    ?rel_uri general_predicate:element element:relation ;
                            relation_predicate:t_id ?rel_tid ;
                            general_predicate:str_id ?rel_strid ;
                            general_predicate:type ?rel_type ;
                            general_predicate:name ?rel_name ;
                            general_predicate:properties ?rel_properties .
                    ?snode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?snode_strid ;
                            general_predicate:type ?snode_type ;
                            general_predicate:name ?snode_name ;
                            general_predicate:properties ?snode_properties .
                    ?enode_uri general_predicate:element element:node ;
                            general_predicate:str_id ?enode_strid ;
                            general_predicate:type ?enode_type ;
                            general_predicate:name ?enode_name ;
                            general_predicate:properties ?enode_properties .
                    FILTER(?snode_strid = "{snode_strid}" && ?snode_type = {snode_type} && ?enode_strid = "{enode_strid}" && ?enode_type = {enode_type})
                }}
            }}
        }}
        '''
        formated_query = select_triplet_query.format(
            element_uriprefix=self.general_uries['element']['prefix'],
            relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
            generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
            named_graph_uri=self.named_graph_uri,
            snode_strid=node1.id, snode_type=f"<{self.general_uries['node']['type']['prefix']}{node1.type.value}>",
            enode_strid=node2.id, enode_type=f"<{self.general_uries['node']['type']['prefix']}{node2.type.value}>"
        )
        # print(formated_query)
        raw_output = self.execute(formated_query)
        formated_triplets = self.parse_query_triplets_output(raw_output)
        return formated_triplets

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        if id_type is None:
            if detailed:
                result = {
                    'triplets': {'simple': 0, 'hyper': 0, 'episodic': 0, 'time': 0},
                    'nodes': {'object': 0, 'hyper': 0, 'episodic': 0, 'time': 0}
                }

                count_nodes_query = '''
                PREFIX element: <{element_uriprefix}>
                PREFIX general_predicate: <{generalpredicate_uriprefix}>
                SELECT ?node_type (COUNT(?node) AS ?count)
                FROM NAMED <{named_graph_uri}>
                WHERE {{
                    GRAPH <{named_graph_uri}> {{
                        ?node general_predicate:element element:node ;
                            general_predicate:type ?node_type .
                    }}
                }} GROUP BY ?node_type
                '''
                formated_query = count_nodes_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    named_graph_uri=self.named_graph_uri,
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                result['nodes'].update({info['node_type'].split('#')[1]: int(info['count']) for info in raw_output})

                count_rels_query = '''
                PREFIX element: <{element_uriprefix}>
                PREFIX general_predicate: <{generalpredicate_uriprefix}>
                SELECT ?rel_type (COUNT(?relation) AS ?count)
                FROM NAMED <{named_graph_uri}>
                WHERE {{
                    GRAPH <{named_graph_uri}> {{
                        ?relation general_predicate:element element:relation ;
                            general_predicate:type ?rel_type .
                    }}
                }} GROUP BY ?rel_type
                '''
                formated_query = count_rels_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    named_graph_uri=self.named_graph_uri,
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                result['triplets'].update({info['rel_type'].split('#')[1]: int(info['count']) for info in raw_output})

            else:
                result = dict()
                count_nodes_query = '''
                PREFIX element: <{element_uriprefix}>
                PREFIX general_predicate: <{generalpredicate_uriprefix}>
                SELECT (COUNT(?node) AS ?nodes_count)
                FROM NAMED <{named_graph_uri}>
                WHERE {{
                    GRAPH <{named_graph_uri}> {{
                        ?node general_predicate:element element:node .
                    }}
                }}
                '''
                formated_query = count_nodes_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    named_graph_uri=self.named_graph_uri,
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                result['nodes'] = [int(info['nodes_count']) for info in raw_output][0]

                count_rels_query = '''
                PREFIX element: <{element_uriprefix}>
                PREFIX general_predicate: <{generalpredicate_uriprefix}>
                SELECT (COUNT(?relation) AS ?rels_count)
                FROM NAMED <{named_graph_uri}>
                WHERE {{
                    GRAPH <{named_graph_uri}> {{
                        ?relation general_predicate:element element:relation .
                    }}
                }}
                '''
                formated_query = count_rels_query.format(
                    element_uriprefix=self.general_uries['element']['prefix'],
                    generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                    named_graph_uri=self.named_graph_uri,
                )
                # print(formated_query)
                raw_output = self.execute(formated_query)
                result['triplets'] = [int(info['rels_count']) for info in raw_output][0]

        elif id_type == 'node':
            count_specnodes_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            SELECT (COUNT(?node) AS ?nodes_count)
            FROM NAMED <{named_graph_uri}>
            WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?node general_predicate:element element:node ;
                        general_predicate:str_id "{str_id}" .
                }}
            }}
            '''
            formated_query = count_specnodes_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                str_id=item_id.id
            )
            # print(formated_query)
            raw_output = self.execute(formated_query)
            result = [int(info['nodes_count']) for info in raw_output][0]

        elif id_type == 'relation':
            count_specrels_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            SELECT (COUNT(?relation) AS ?rels_count)
            FROM NAMED <{named_graph_uri}>
            WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?relation general_predicate:element element:relation ;
                        general_predicate:str_id "{str_id}" .
                }}
            }}
            '''
            formated_query = count_specrels_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                str_id=item_id.id
            )
            # print(formated_query)
            raw_output = self.execute(formated_query)
            result = [int(info['rels_count']) for info in raw_output][0]

        elif id_type == 'triplet':
            count_spectriplets_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            PREFIX relation_predicate: <{relationpredicate_uriprefix}>
            SELECT (COUNT(?relation) AS ?rels_count)
            FROM NAMED <{named_graph_uri}>
            WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?relation general_predicate:element element:relation ;
                        relation_predicate:t_id "{t_id}" .
                }}
            }}
            '''
            formated_query = count_spectriplets_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                named_graph_uri=self.named_graph_uri,
                t_id=item_id
            )
            # print(formated_query)
            raw_output = self.execute(formated_query)
            result = [int(info['rels_count']) for info in raw_output][0]

        else:
            raise ValueError(f"id_type: {id_type}")

        return result

    @restore_connection
    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        if not isinstance(item_id, str):
            if type(item_id) in [NodeInfo, RelationInfo]:
                if not isinstance(item_id.id, str):
                    raise ValueError(f"item_id: {item_id}")
            else:
                raise ValueError(f"item_id: {item_id}")

        formated_query = None

        if id_type == 'node':
            is_nodeexist_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            ASK WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?node general_predicate:element element:node ;
                          general_predicate:str_id "{str_id}" ;
                          general_predicate:type {type} .
                }}
            }}
            '''
            formated_query = is_nodeexist_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                str_id=item_id.id,
                type=f"<{self.general_uries['node']['type']['prefix']}{item_id.type.value}>"
            )
            # print(formated_query)

        elif id_type == 'relation':
            is_relexist_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            ASK WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?relation general_predicate:element element:relation ;
                              general_predicate:str_id "{str_id}" ;
                              general_predicate:type {type} .
                }}
            }}
            '''
            formated_query = is_relexist_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                named_graph_uri=self.named_graph_uri,
                str_id=item_id.id,
                type=f"<{self.general_uries['relation']['type']['prefix']}{item_id.type.value}>"
            )
            # print(formated_query)

        elif id_type == 'triplet':
            is_tripletexist_query = '''
            PREFIX element: <{element_uriprefix}>
            PREFIX general_predicate: <{generalpredicate_uriprefix}>
            PREFIX relation_predicate: <{relationpredicate_uriprefix}>
            ASK WHERE {{
                GRAPH <{named_graph_uri}> {{
                    ?relation general_predicate:element element:relation ;
                              relation_predicate:t_id "{t_id}" .
                }}
            }}
            '''
            formated_query = is_tripletexist_query.format(
                element_uriprefix=self.general_uries['element']['prefix'],
                generalpredicate_uriprefix=self.general_uries['general_fields']['prefix'],
                relationpredicate_uriprefix=self.general_uries['relation']['field_prefix'],
                named_graph_uri=self.named_graph_uri,
                t_id=item_id
            )
            # print(formated_query)

        else:
            raise ValueError(f"id_type: {id_type}")

        output = self.execute(formated_query)
        formated_output = bool(output)

        return formated_output

    @restore_connection
    def clear(self) -> None:
        sparql_query = f"CLEAR GRAPH <{self.named_graph_uri}>"
        # print(sparql_query)
        self.execute(sparql_query, 'write')
