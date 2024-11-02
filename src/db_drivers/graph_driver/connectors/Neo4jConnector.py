import copy
from neo4j import GraphDatabase
from typing import List, Dict, Tuple
from tqdm import tqdm
from abc import ABC, abstractmethod
import json
from dataclasses import dataclass

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.data_structs import Triplet, Node, Relation, TripletCreator, NodeCreator, NodeType, NODES_TYPES_MAP, RELATIONS_TYPES_MAP

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
        """_summary_

        :param node: _description_
        :type node: Node
        :return: _description_
        :rtype: str
        """
        query_props = {}
        for prop_name, prop_value in node.prop.items():
            p_name, p_value = prop_name.replace(" ", "_"), json.dumps(prop_value, ensure_ascii=False)
            query_props[p_name] = p_value

        query_props['name'] = json.dumps(node.name, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in query_props.items()])
        query = f"CREATE (n:{node.type.value} " + "{" + str_props + "}) RETURN elementId(n) as node_id"
        return query


    def create_rel_query(self, triplet: Triplet) -> str:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        :return: _description_
        :rtype: str
        """
        rel_props = {}
        for prop_name, prop_value in triplet.relation.prop.items():
            p_name, p_value = prop_name.replace(' ', '_'), json.dumps(prop_value, ensure_ascii=False)
            rel_props[p_name] = p_value

        rel_props['name'] = json.dumps(triplet.relation.name, ensure_ascii=False)
        rel_props['str_id'] = json.dumps(triplet.id, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in rel_props.items()])
        subj_t, subj_id = triplet.start_node.type.value, triplet.start_node.id
        obj_t, obj_id = triplet.end_node.type.value, triplet.end_node.id
        rel_t = triplet.relation.type.value
        query = ""
        query += f'MATCH (subj:{subj_t}), (obj:{obj_t}) WHERE elementId(subj) = "{subj_id}" AND elementId(obj) = "{obj_id}" '
        query += f'CREATE (subj)-[rel:{rel_t}' + '{' + str_props + '}' + ']->(obj) '
        query += 'RETURN elementId(rel) as rel_id'
        return query

    def create_triplet(self, triplet: Triplet) -> Tuple[int,int]:
        # add nodes and edges which presented in triplets list
        # Check to unique node name
        # Pay attention to the format of triplets
        created_nodes_count, created_rels_count = 0,0

        #
        subj_str_id, subj_t = triplet.start_node.prop['str_id'], triplet.start_node.type.value
        subj_out = self.execute_query(f'MATCH (subj:{subj_t}) WHERE subj.str_id = "{subj_str_id}" RETURN elementID(subj) as node_id')
        if len(subj_out) < 1:
            created_nodes_count += 1
            insert_subj_query = self.create_node_query(triplet.start_node)
            triplet.start_node.id = self.execute_query(insert_subj_query)[0]['node_id']
        else:
            triplet.start_node.id = subj_out[0]['node_id']

        #
        obj_str_id, obj_t = triplet.end_node.prop['str_id'], triplet.end_node.type.value
        obj_out = self.execute_query(f'MATCH (obj:{obj_t}) WHERE obj.str_id = "{obj_str_id}" RETURN elementID(obj) as node_id')
        if len(obj_out) < 1:
            created_nodes_count += 1
            insert_obj_query = self.create_node_query(triplet.end_node)
            triplet.end_node.id = self.execute_query(insert_obj_query)[0]['node_id']
        else:
            triplet.end_node.id = obj_out[0]['node_id']

        #
        rel_str_id, rel_t = triplet.id, triplet.relation.type.value
        rel_out = self.execute_query(f'MATCH (a)-[rel:{rel_t}]->(b) WHERE elementId(a) = "{triplet.start_node.id}" AND elementId(b) = "{triplet.end_node.id}" AND rel.str_id = "{rel_str_id}" RETURN elementID(rel) as rel_id')
        if len(rel_out) < 1:
            created_rels_count += 1
            rel_query = self.create_rel_query(triplet)
            triplet.relation.id = self.execute_query(rel_query)[0]['rel_id']
        else:
            triplet.relation.id = rel_out[0]['rel_id']

        return created_nodes_count, created_rels_count

    # TODO
    def delete_triplet(self, triplet: Triplet) -> None:
        pass

    def execute_query(self, query: str, db_flag: bool = True):
        """_summary_

        :param query: _description_
        :type query: str
        :param db_flag: _description_, defaults to True
        :type db_flag: bool, optional
        :return: _description_
        :rtype: _type_
        """
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

    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        raw_nodes = self.execute_query(
            f'MATCH (a)-[r]-(b) WHERE elementId(a) = "{base_node_id}" AND elementId(b) <> "{parent_node_id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b'].element_id for node in raw_nodes]
        return formated_nodes

    def parse_query_output(self, output):
        """_summary_

        :param output: _description_
        :type output: _type_
        :return: _description_
        :rtype: _type_
        """
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

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        output = self.execute_query(
            f'MATCH (n1)-[rel]-(n2) WHERE elementId(n1) = "{node1_id}" AND elementId(n2) = "{node2_id}" RETURN n1, rel, n2')

        formatted_triplets = self.parse_query_output(output)
        return formatted_triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        formatted_triplets = []
        if subj_names:
            for subj_name in subj_names:
                output = self.execute_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n1.name) = LOWER("{subj_name}") RETURN n1, rel, n2')
                formatted_triplets += self.parse_query_output(output)
        elif obj_names:
            for obj_name in obj_names:
                output = self.execute_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n2.name) = LOWER("{obj_name}") RETURN n1, rel, n2')
                formatted_triplets += self.parse_query_output(output)
        else:
            output = self.execute_query(
                f'MATCH (n1:object)-[rel]-(n2:{obj_type}) RETURN n1, rel, n2')
            formatted_triplets += self.parse_query_output(output)
        return formatted_triplets

    def count_instances(self) -> int:
        # TODO
        pass
