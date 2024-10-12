import copy
from neo4j import GraphDatabase
from typing import List, Dict, Tuple
from tqdm import tqdm
from abc import ABC, abstractmethod
import json
from dataclasses import dataclass

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.data_structs import Triplet, Node, Relation, TripletCreator, NodeCreator, NODES_TYPES_MAP, RELATIONS_TYPES_MAP

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(uri="bolt://localhost:7687", params={'user': "neo4j", 'pwd': 'password', 'db_name': 'testdb'})

class Neo4jConnector(AbstractGraphDatabaseConnection):
    def __init__(self, config: GraphDBConnectionConfig):
        self.config = config
        self.open_connection()

        self.execute_query(f'CREATE DATABASE {self.config.params["db_name"]} IF NOT EXISTS', db_flag=False)
        self.create_node_template = 'CREATE (n:{type} {{ name: "{name}"}})'
        self.create_rel_template0 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name}]->(b)"""
        self.create_rel_template1 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name}: "{rel_prop_value}"}}]->(b)"""
        self.create_rel_template2 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name1}: "{rel_prop_value1}", {rel_prop_name2}: "{rel_prop_value2}"}}]->(b)"""
        self.create_rel_template5 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name1}: "{rel_prop_value1}", {rel_prop_name2}: "{rel_prop_value2}", {rel_prop_name3}: "{rel_prop_value3}", {rel_prop_name4}: "{rel_prop_value4}", {rel_prop_name5}: "{rel_prop_value5}"}}]->(b)"""

        self.extract_node_type_template = 'MATCH (a:{type}) RETURN a'
        self.extract_node_name_template = 'MATCH (a) WHERE a.name="{name}" RETURN a'
        self.extract_node_type_name_template = 'MATCH (a:{type}) WHERE a.name="{name}" RETURN a'

        # MATCH (a:User {username: 'user6'})-[r]-(b) RETURN r, a, b
        self.extract_triplets_name1_template = 'MATCH (a)-[r]-(b) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_template = 'MATCH (a)-[r]-(b) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_names_template = 'MATCH (a)-[r]-(b) WHERE a.name="{name1}" AND b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_name1_rel_template = 'MATCH (a)-[r:{rel}]-(b) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_rel_template = 'MATCH (a)-[r:{rel}]-(b) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_rel_template = 'MATCH (a)-[r:{rel}]-(b) RETURN a, r, b'
        self.extract_triplets_rel_prop_template = 'MATCH (a)-[r]-(b) WHERE r.{prop_name}="{prop_value}" RETURN a, r, b'

    def open_connection(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.config.uri, auth=(self.config.params['user'], self.config.params['pwd']))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close_connection(self):
        if self.driver is not None:
            self.driver.close()

    def create_node_query(self, node: Node) -> str:
        query_props = {}
        for prop_name, prop_value in node.prop.items():
            p_name, p_value = prop_name.replace(" ", "_"), json.dumps(prop_value, ensure_ascii=False)
            query_props[p_name] = p_value

        node_name = json.dumps(node.name, ensure_ascii=False)
        query_props['name'] = node_name

        str_props = ", ".join([f"{k}: {v}" for k, v in query_props.items()])
        query = f"CREATE (n:{node.type.value} " + "{" + str_props + "}) RETURN elementId(n) as node_id"
        return query

    
    def create_rel_query(self, triplet: Triplet) -> str:
        rel_props = {}
        for prop_name, prop_value in triplet.relation.prop.items():
            p_name, p_value = prop_name.replace(' ', '_'), json.dumps(prop_value, ensure_ascii=False)
            rel_props[p_name] = p_value

        rel_name = json.dumps(triplet.relation.name, ensure_ascii=False)
        rel_props['name'] = rel_name 
        
        query = ""
        str_props = ", ".join([f"{k}: {v}" for k, v in rel_props.items()])
        subj_t, subj_id = triplet.start_node.type.value, triplet.start_node.id
        obj_t, obj_id = triplet.end_node.type.value, triplet.end_node.id
        rel_t = triplet.relation.type.value
        query += f'MATCH (subj:{subj_t}), (obj:{obj_t}) WHERE elementId(subj) = "{subj_id}" AND elementId(obj) = "{obj_id}" '
        query += f'CREATE (subj)-[rel:{rel_t}' + '{' + str_props + '}' + ']->(obj) '
        query += 'RETURN elementId(rel) as rel_id'
        return query

    def create_triplet(self, triplet: Triplet) -> Tuple[int,int]:
        # add nodes and edges which presented in triplets list
        # Check to unique node name
        # Pay attention to the format of triplets
        
        created_nodes_count, created_rels_count = 0,0
        subj_n, subj_t = json.dumps(triplet.start_node.name, ensure_ascii=False), triplet.start_node.type.value
        subj_out = self.execute_query(f'MATCH (subj:{subj_t}) WHERE subj.name = {subj_n} RETURN elementID(subj) as node_id')
        if len(subj_out) < 1:
            created_nodes_count += 1
            insert_subj_query = self.create_node_query(triplet.start_node)
            triplet.start_node.id = self.execute_query(insert_subj_query)[0]['node_id']
        else:
            triplet.start_node.id = subj_out[0]['node_id']
        
        obj_n, obj_t = json.dumps(triplet.end_node.name, ensure_ascii=False), triplet.end_node.type.value
        obj_out = self.execute_query(f'MATCH (obj:{obj_t}) WHERE obj.name = {obj_n} RETURN elementID(obj) as node_id')
        if len(obj_out) < 1:
            created_nodes_count += 1
            insert_obj_query = self.create_node_query(triplet.end_node)
            triplet.end_node.id = self.execute_query(insert_obj_query)[0]['node_id']
        else:
            triplet.end_node.id = obj_out[0]['node_id']
        
        created_rels_count += 1
        rel_query = self.create_rel_query(triplet)
        triplet.relation.id = self.execute_query(rel_query)[0]['rel_id']

        return created_nodes_count, created_rels_count

    # TODO
    def delete_triplet(self, triplet: Triplet) -> None:
        pass

    def execute_query(self, query: str, db_flag: bool = True):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=self.config.params['db_name']) if db_flag else self.driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
            print("Error query: ", query)
        finally:
            if session is not None:
                session.close()
        return response
    
    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: str) -> List[str]:
        raw_nodes = self.execute_query(
            f'MATCH (a)-[r]-(b) WHERE elementId(a) = "{base_node_id}" AND elementId(b) <> "{parent_node_id}" AND ANY(lbl in {accepted_n_types} where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b'].element_id for node in raw_nodes]
        return formated_nodes
    
    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        output = self.execute_query(
            f'MATCH (n1)-[rel]-(n2) WHERE elementId(n1) = "{node1_id}" AND elementId(n2) = "{node2_id}" RETURN n1, rel, n2')
        
        formated_triplets = []
        for raw_triplet in output:
            node1 = NodeCreator.create(id=raw_triplet['n1'].element_id, name=str(raw_triplet['n1']['name']), 
                                            type=NODES_TYPES_MAP[list(raw_triplet['n1'].labels)[0]],
                                            prop=dict(raw_triplet['n1']))
            node2 = NodeCreator.create(id=raw_triplet['n2'].element_id, name=str(raw_triplet['n2']['name']), 
                                            type=NODES_TYPES_MAP[list(raw_triplet['n2'].labels)[0]],
                                            prop=dict(raw_triplet['n2']))
            relation = Relation(id=raw_triplet['rel'].element_id, name=str(raw_triplet['rel']['name']), 
                                type=RELATIONS_TYPES_MAP[raw_triplet['rel'].type], 
                                prop=dict(raw_triplet['rel']))
            
            start_node_id = raw_triplet['rel'].nodes[0].element_id
            start_node, end_node = (node1, node2) if start_node_id == node1.id else (node2, node1)
            triplet = TripletCreator.create(start_node, relation, end_node, add_stringified_triplet=False)
            formated_triplets.append(triplet)
        return formated_triplets