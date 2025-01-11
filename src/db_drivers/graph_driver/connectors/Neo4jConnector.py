from neo4j import GraphDatabase
from typing import List, Dict, Union
import json

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.data_structs import Triplet, Node, Relation, TripletCreator, NodeCreator, NodeType, RelationCreator, RelationType, NODES_TYPES_MAP, RELATIONS_TYPES_MAP

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(uri="bolt://localhost:7687", params={'user': "neo4j", 'pwd': 'password'})

class Neo4jConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: GraphDBConnectionConfig = DEFAULT_NEO4J_CONFIG):
        self.config = config
        self.open_connection()

        self.execute_query(f'CREATE DATABASE {self.config.db_info["db"]} IF NOT EXISTS', db_flag=False)
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

        if self.config.need_to_clear:
            self.clear()

    def open_connection(self) -> None:
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.config.uri, auth=(self.config.params['user'], self.config.params['pwd']))
        except Exception as e:
            print("Failed to create the driver:", e)

    def is_open(self) -> None:
        # TODO
        pass

    def close_connection(self) -> None:
        if self.driver is not None:
            self.driver.close()

    def create_node_query(self, node: Node) -> str:
        query_props = {}
        for prop_name, prop_value in node.prop.items():
            p_name, p_value = prop_name.replace(" ", "_"), json.dumps(prop_value, ensure_ascii=False)
            query_props[p_name] = p_value

        query_props['name'] = json.dumps(node.name, ensure_ascii=False)
        query_props['str_id'] = json.dumps(node.id, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in query_props.items()])
        query = f"CREATE (n:{node.type.value} " + "{" + str_props + "}) RETURN elementId(n) as node_id"
        return query


    def create_rel_query(self, triplet: Triplet) -> str:
        rel_props = {}
        for prop_name, prop_value in triplet.relation.prop.items():
            p_name, p_value = prop_name.replace(' ', '_'), json.dumps(prop_value, ensure_ascii=False)
            rel_props[p_name] = p_value

        rel_props['name'] = json.dumps(triplet.relation.name, ensure_ascii=False)
        rel_props['t_id'] = json.dumps(triplet.id, ensure_ascii=False)
        rel_props['str_id'] = json.dumps(triplet.relation.id, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in rel_props.items()])
        subj_t, subj_id = triplet.start_node.type.value, triplet.start_node.id
        obj_t, obj_id = triplet.end_node.type.value, triplet.end_node.id
        rel_t = triplet.relation.type.value
        query = ""
        query += f'MATCH (subj:{subj_t}), (obj:{obj_t}) WHERE subj.str_id = "{subj_id}" AND obj.str_id = "{obj_id}" '
        query += f'CREATE (subj)-[rel:{rel_t}' + '{' + str_props + '}' + ']->(obj) '
        query += 'RETURN elementId(rel) as rel_id'
        return query

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if type(triplet.id) is not str:
                raise ValueError
        unique_ids = set(map(lambda triplet: triplet.id, triplets))
        if len(triplets) != len(unique_ids):
            raise ValueError

        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)
            if cur_info is None or cur_info['s_node']:
                insert_subj_query = self.create_node_query(triplet.start_node)
                self.execute_query(insert_subj_query)
            if cur_info is None or cur_info['e_node']:
                insert_obj_query = self.create_node_query(triplet.end_node)
                self.execute_query(insert_obj_query)

            insert_rel_query = self.create_rel_query(triplet)
            self.execute_query(insert_rel_query)


    def read(self, ids: List[str]) -> List[Triplet]:
        str_ids = '['+', '.join(list(map(lambda id: f'"{id}"', ids))) + ']'
        query = f"MATCH (n1)-[rel]->(n2) WHERE any(id IN {str_ids} WHERE rel.t_id = id) RETURN n1, rel, n2"
        raw_output = self.execute_query(query)
        triplets = self.parse_query_triplets_output(raw_output)
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str], delete_info: Dict[int,Dict[str,bool]] = dict()) -> None:
        for i, t_id in enumerate(ids):
            cur_info = delete_info.get(i, None)
            delete_statement = ['rel']

            if cur_info is None or cur_info['s_node']:
                delete_statement.append('s_node')

            if cur_info is None or cur_info['e_node']:
                delete_statement.append('e_node')

            delete_statement = ', '.join(delete_statement)

            self.execute_query(f'MATCH (s_node)-[rel]->(e_node) WHERE rel.t_id = "{t_id}" DELETE {delete_statement}')

    def read_by_name(self, name: str, type: Union[RelationType, NodeType], object: str = 'triplet') -> List[Union[Triplet, Node]]:
        dump_name = json.dumps(name, ensure_ascii=False)
        if object == 'triplet':
            output = self.execute_query(f'MATCH (n1)-[rel:{type.value}]->(n2) WHERE rel.name = {dump_name} RETURN n1,rel,n2;')
            formated_output = self.parse_query_triplets_output(output)
        elif object == 'node':
            output = self.execute_query(f'MATCH (n:{type.value}) WHERE n.name = {dump_name} RETURN n;')
            formated_output = self.parse_query_nodes_output(output)
        else:
            raise ValueError

        return formated_output

    def execute_query(self, query: str, db_flag: bool = True) -> List[object]:
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=self.config.db_info['db']) if db_flag else self.driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
            print("Error query: ", query)
        finally:
            if session is not None:
                session.close()
        return response

    def get_adjecent_nodes(self, base_node_id: str,
            accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[str]:
        if type(base_node_id) is not str:
            raise ValueError

        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        raw_nodes = self.execute_query(
            f'MATCH (a)-[r]-(b) WHERE a.str_id = "{base_node_id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b']['str_id'] for node in raw_nodes]
        return formated_nodes

    def parse_query_nodes_output(self, output: List[object]) -> List[Node]:
        formated_nodes = []
        for raw_node in output:

            n_dict = dict(raw_node['n'])
            for k,v in n_dict.items():
                try:
                    n_dict[k] = json.loads(v)
                except json.decoder.JSONDecodeError as e:
                    pass

            node = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(raw_node['n'].labels)[0]],
                name=n_dict['name'], prop={**n_dict})

            formated_nodes.append(node)
        return formated_nodes

    def parse_query_triplets_output(self, output: List[object]) -> List[Triplet]:
        formated_triplets = []
        for raw_triplet in output:

            n1_dict = dict(raw_triplet['n1'])
            n2_dict = dict(raw_triplet['n2'])
            rel_dict = dict(raw_triplet['rel'])

            node1 = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(raw_triplet['n1'].labels)[0]],
                name=n1_dict['name'], prop=n1_dict, add_stringified_node=False)

            node2 = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(raw_triplet['n2'].labels)[0]],
                name=n2_dict['name'], prop=n2_dict, add_stringified_node=False)

            relation = RelationCreator.create(
                r_type=RELATIONS_TYPES_MAP[raw_triplet['rel'].type],
                name=rel_dict['name'], prop=rel_dict)

            start_node_id = raw_triplet['rel'].nodes[0].element_id
            if start_node_id == raw_triplet['n1'].element_id:
                start_node, end_node = (node1, node2)
            elif start_node_id == raw_triplet['n2'].element_id:
                start_node, end_node = (node2, node1)
            else:
                raise ValueError

            triplet = TripletCreator.create(
                start_node, relation, end_node, add_stringified_triplet=True)
            formated_triplets.append(triplet)

        # print("PARSED_TRIPLETS: ")
        # for triplet in formated_triplets:
        #     print(f"* triplet_id = {triplet.id}")
        #     print(f"\t s_node: id = {triplet.start_node.id}; str_id = {triplet.start_node.prop['str_id']}")
        #     print(f"\t rel: id = {triplet.relation.id}; t_id = {triplet.relation.prop['t_id']} str_id = {triplet.relation.prop['str_id']}")
        #     print(f"\t e_node: id = {triplet.end_node.id}; str_id = {triplet.end_node.prop['str_id']}")

        return formated_triplets

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        if (type(node1_id) is not str) or (type(node2_id) is not str):
            raise ValueError
        if (not self.item_exist(node1_id, id_type='node')) or (not self.item_exist(node2_id, id_type='node')):
            raise ValueError

        output = self.execute_query(
            f'MATCH (n1)-[rel]-(n2) WHERE n1.str_id = "{node1_id}" AND n2.str_id = "{node2_id}" RETURN n1, rel, n2')

        formated_triplets = self.parse_query_triplets_output(output)
        return formated_triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        formated_triplets = []
        if subj_names:
            for subj_name in subj_names:
                subj_dump = json.dumps(subj_name, ensure_ascii=False)
                output = self.execute_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n1.name) = LOWER({subj_dump}) RETURN n1, rel, n2')
                formated_triplets += self.parse_query_triplets_output(output)
        elif obj_names:
            for obj_name in obj_names:
                obj_dump = json.dumps(obj_name, ensure_ascii=False)
                output = self.execute_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n2.name) = LOWER({obj_dump}) RETURN n1, rel, n2')
                formated_triplets += self.parse_query_triplets_output(output)
        else:
            output = self.execute_query(
                f'MATCH (n1:object)-[rel]-(n2:{obj_type}) RETURN n1, rel, n2')
            formated_triplets += self.parse_query_triplets_output(output)

        return formated_triplets

    def count_items(self, id: str = None, id_type: str = None) -> Union[Dict[str,int],int]:
        if id_type is None:
            n_output = self.execute_query("MATCH (a) RETURN count(a) as n_count")[0]
            r_output = self.execute_query("MATCH (a)-[rel]->(b) RETURN count(rel) as r_count")[0]
            result = {'triplets': r_output['r_count'], 'nodes': n_output['n_count']}

        elif id_type == 'node':
            n_output = self.execute_query(f'MATCH (a) WHERE a.str_id = "{id}" RETURN count(a) as n_count')[0]
            result = n_output['n_count']

        elif id_type == 'relation':
            r_output = self.execute_query(f'MATCH (a)-[rel]->(b) WHERE rel.str_id = "{id}" RETURN count(rel) as r_count')[0]
            result = r_output['r_count']

        elif id_type == 'triplet':
            r_output = self.execute_query(f'MATCH (a)-[rel]->(b) WHERE rel.t_id = "{id}" RETURN count(rel) as r_count')[0]
            result = r_output['r_count']

        else:
            raise ValueError

        return result

    def item_exist(self, id: str, id_type='triplet') -> bool:
        if type(id) is not str:
            raise ValueError

        if id_type == 'node':
            query = f'MATCH (n) WHERE n.str_id = "{id}" RETURN n'
        elif id_type == 'relation':
            query = f'MATCH (n1)-[rel]-(n2) WHERE rel.str_id = "{id}" RETURN rel'
        elif id_type == 'triplet':
            query = f'MATCH (n1)-[rel]-(n2) WHERE rel.t_id = "{id}" RETURN rel'
        else:
            raise ValueError

        output = self.execute_query(query)
        return len(output) > 0

    def clear(self) -> None:
        self.execute_query("MATCH (n)-[rel]->() DELETE n,rel")
        self.execute_query("MATCH (n) DELETE n")
