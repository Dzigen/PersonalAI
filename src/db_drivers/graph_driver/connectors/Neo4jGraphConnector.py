from neo4j import GraphDatabase
from typing import List, Dict, Union
import json

from .configs import DEFAULT_NEO4J_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.data_structs import Triplet, Node, TripletCreator, NodeCreator, \
    NodeType, RelationCreator, RelationType, NODES_TYPES_MAP, RELATIONS_TYPES_MAP, \
    NodeInfo, RelationInfo


class Neo4jGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_NEO4J_CONFIG):
        if isinstance(config, dict):
            config = GraphDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: GraphDBConnectionConfig = config

    def open_connection(self) -> None:
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                f"bolt://{self.config.host}:{self.config.port}",
                auth=(self.config.params['user'], self.config.params['pwd']))
        except Exception as e:
            print("Failed to create the driver:", e)

        #
        self.execute_query(
            f'CREATE DATABASE {self.config.db_info["db"]}{self.config.db_info["table"]} IF NOT EXISTS', db_flag=False)

        # Creating indexes
        if self.config.create_index:
            cquery_statements = [
                "CREATE INDEX name_object_node IF NOT EXISTS FOR (n:object) ON n.nam;",
                "CREATE INDEX name_hyper_node IF NOT EXISTS FOR (n:hyper) ON n.name;",
                "CREATE INDEX name_episodic_node IF NOT EXISTS FOR (n:episodic) ON n.name;",
                "CREATE INDEX strid_object_node IF NOT EXISTS FOR (n:object) ON n.str_id;",
                "CREATE INDEX strid_hyper_node IF NOT EXISTS FOR (n:hyper) ON n.str_id;",
                "CREATE INDEX strid_episodic_node IF NOT EXISTS FOR (n:episodic) ON n.str_id;",
                "CREATE INDEX strid_simple_relation IF NOT EXISTS FOR ()-[r:simple]->() ON r.str_id;",
                "CREATE INDEX strid_hyper_relation IF NOT EXISTS FOR ()-[r:hyper]->() ON r.str_id; ",
                "CREATE INDEX strid_episodic_relation IF NOT EXISTS FOR ()-[r:episodic]->() ON r.str_id;",
                "CREATE INDEX tid_simple_relation IF NOT EXISTS FOR ()-[r:simple]->() ON r.t_id",
                "CREATE INDEX tid_hyper_relation IF NOT EXISTS FOR ()-[r:hyper]->() ON r.t_id",
                "CREATE INDEX tid_episodic_relation IF NOT EXISTS FOR ()-[r:episodic]->() ON r.t_id",
                "CREATE INDEX name_simple_relation IF NOT EXISTS FOR ()-[r:simple]->() ON r.name",
                "CREATE INDEX name_hyper_relation IF NOT EXISTS FOR ()-[r:hyper]->() ON r.name",
                "CREATE INDEX name_episodic_relation IF NOT EXISTS FOR ()-[r:episodic]->() ON r.name"]
            for cqueru in cquery_statements:
                self.execute_query(cqueru)

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> None:
        # TODO
        raise NotImplementedError

    def close_connection(self) -> None:
        try:
            self.driver.close()
        except TypeError:
            pass

    def __del__(self):
        self.close_connection()

    def create_node_query(self, node: Node) -> str:
        query_props = {}
        for prop_name, prop_value in node.prop.items():
            p_name, p_value = prop_name.replace(
                " ", "_"), json.dumps(prop_value, ensure_ascii=False)
            query_props[p_name] = p_value

        query_props['name'] = json.dumps(node.name, ensure_ascii=False)
        query_props['str_id'] = json.dumps(node.id, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in query_props.items()])
        query = f"CREATE (n:{node.type.value} " + "{" + \
            str_props + "}) RETURN elementId(n) as node_id"
        return query

    def create_rel_query(self, triplet: Triplet) -> str:
        rel_props = {}
        for prop_name, prop_value in triplet.relation.prop.items():
            p_name, p_value = prop_name.replace(
                ' ', '_'), json.dumps(prop_value, ensure_ascii=False)
            rel_props[p_name] = p_value

        rel_props['name'] = json.dumps(
            triplet.relation.name, ensure_ascii=False)
        rel_props['t_id'] = json.dumps(triplet.id, ensure_ascii=False)
        rel_props['str_id'] = json.dumps(
            triplet.relation.id, ensure_ascii=False)

        str_props = ", ".join([f"{k}: {v}" for k, v in rel_props.items()])
        subj_t, subj_id = triplet.start_node.type.value, triplet.start_node.id
        obj_t, obj_id = triplet.end_node.type.value, triplet.end_node.id
        rel_t = triplet.relation.type.value
        query = ""
        query += f'MATCH (subj:{subj_t}), (obj:{obj_t}) WHERE subj.str_id = "{subj_id}" AND obj.str_id = "{obj_id}" '
        query += f'CREATE (subj)-[rel:{rel_t}' + \
            '{' + str_props + '}' + ']->(obj) '
        query += 'RETURN elementId(rel) as rel_id'
        return query

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if not isinstance(triplet.id, str):
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
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError

        str_ids = '[' + ', '.join(list(map(lambda id: f'"{id}"', ids))) + ']'
        query = f"MATCH (n1)-[rel]->(n2) WHERE any(id IN {str_ids} WHERE rel.t_id = id) RETURN n1, rel, n2"
        raw_output = self.execute_query(query)
        triplets = self.parse_query_triplets_output(raw_output)
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError

        for i, t_id in enumerate(ids):
            cur_info = delete_info.get(i, None)
            nodes_to_delete = []

            if cur_info is None or cur_info['s_node']:
                nodes_to_delete.append('sn')

            if cur_info is None or cur_info['e_node']:
                nodes_to_delete.append('en')

            output = self.execute_query(
                f'MATCH (s_node)-[rel]->(e_node) WHERE rel.t_id = "{t_id}" DELETE rel \
                    RETURN elementId(s_node) as sn_id, labels(s_node) as sn_labels, elementId(e_node) as en_id, labels(e_node) as en_labels')
            if len(output) < 1:
                continue

            assert len(output) == 1

            if len(nodes_to_delete) > 0:
                where_statement = []
                for n_name in nodes_to_delete:
                    where_statement.append(
                        f'(elementId(n) = "{output[0][f"{n_name}_id"]}" and n:{list(output[0][f"{n_name}_labels"])[0]})')
                where_statement = ' or '.join(where_statement)
                self.execute_query(f'MATCH (n) WHERE {where_statement} DELETE n')

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        if type(object_type) not in [RelationType, NodeType]:
            raise ValueError

        if not isinstance(name, str):
            raise ValueError

        if len(name) < 1:
            raise ValueError

        dump_name = json.dumps(name, ensure_ascii=False)
        if object == 'relation':
            output = self.execute_query(
                f'MATCH (n1)-[rel:{object_type.value}]->(n2) WHERE rel.name = {dump_name} RETURN n1,rel,n2;')
            formated_output = self.parse_query_triplets_output(output)
        elif object == 'node':
            output = self.execute_query(
                f'MATCH (n:{object_type.value}) WHERE n.name = {dump_name} RETURN n;')
            formated_output = self.parse_query_nodes_output(output)
        else:
            raise ValueError

        return formated_output

    def execute_query(self, query: str, db_flag: bool = True) -> List[object]:
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(
                database=f"{self.config.db_info['db']}{self.config.db_info['table']}") if db_flag else self.driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
            print("Error query: ", query)
        finally:
            if session is not None:
                session.close()
        return response

    def get_adjecent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError

        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        raw_nodes = self.execute_query(
            f'MATCH (a:{base_node.type.value})-[r]-(b) WHERE a.str_id = "{base_node.id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(b)) RETURN b')
        formated_nodes = [NodeInfo(id=node['b']['str_id'], type=NODES_TYPES_MAP[list(node['b'].labels)[0]]) for node in raw_nodes]
        return formated_nodes

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(node1, node2)
        if not isinstance(id_type, str):
            raise ValueError(id_type)

        if id_type == 'triplet':
            str_return_info = 'r.t_id as t_id'
        elif id_type == 'relation':
            str_return_info = 'r.str_id as r_id'
        elif id_type == 'both':
            str_return_info = 'r.t_id as t_id, r.str_id as r_id'
        else:
            raise ValueError(id_type)

        raw_rels = self.execute_query(
            f'MATCH (a:{node1.type.value})-[r]-(b:{node2.type.value}) WHERE a.str_id = "{node1.id}" AND b.str_id = "{node2.id}" RETURN {str_return_info};')

        formated_info = []
        for raw_rel in raw_rels:
            tmp_info = dict()
            if id_type in ['both', 'triplet']:
                tmp_info['t_id'] = raw_rel['t_id']

            if id_type in ['both', 'relation']:
                tmp_info['r_id'] = raw_rel['r_id']

            formated_info.append(tmp_info)

        return formated_info

    # TO THINK (do we need field serialization because we do json.dumps)
    def _load_dumped_dict(self, raw_dict: dict) -> Dict:
        loaded_dict = dict()
        for k, v in raw_dict.items():
            try:
                loaded_dict[k] = json.loads(v)
            except json.decoder.JSONDecodeError as e:
                loaded_dict[k] = v
        return loaded_dict

    def parse_query_nodes_output(self, output: List[object]) -> List[Node]:
        formated_nodes = []
        for raw_node in output:

            n_dict = dict(raw_node['n'])

            node = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(raw_node['n'].labels)[0]],
                name=n_dict['name'], prop={**n_dict})
            del node.prop['name']

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
            del node1.prop['name']

            node2 = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(raw_triplet['n2'].labels)[0]],
                name=n2_dict['name'], prop=n2_dict, add_stringified_node=False)
            del node2.prop['name']

            relation = RelationCreator.create(
                r_type=RELATIONS_TYPES_MAP[raw_triplet['rel'].type],
                name=rel_dict['name'], prop=rel_dict)
            del relation.prop['name']

            start_node_id = raw_triplet['rel'].nodes[0].element_id
            if start_node_id == raw_triplet['n1'].element_id:
                start_node, end_node = (node1, node2)
            elif start_node_id == raw_triplet['n2'].element_id:
                start_node, end_node = (node2, node1)
            else:
                raise ValueError

            triplet = TripletCreator.create(
                start_node, relation, end_node,
                add_stringified_triplet=True, t_id=relation.prop['t_id']
            )
            formated_triplets.append(triplet)

        # print("PARSED_TRIPLETS: ")
        # for triplet in formated_triplets:
        #     print(f"* triplet_id = {triplet.id}")
        #     print(f"\t s_node: id = {triplet.start_node.id}; str_id = {triplet.start_node.prop['str_id']}")
        #     print(f"\t rel: id = {triplet.relation.id}; t_id = {triplet.relation.prop['t_id']} str_id = {triplet.relation.prop['str_id']}")
        #     print(f"\t e_node: id = {triplet.end_node.id}; str_id = {triplet.end_node.prop['str_id']}")

        return formated_triplets

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError
        if (not self.item_exist(node1, 'node')) or (not self.item_exist(node2, 'node')):
            raise ValueError

        output = self.execute_query(
            f'MATCH (n1:{node1.type.value})-[rel]-(n2:{node2.type.value}) WHERE n1.str_id = "{node1.id}" AND n2.str_id = "{node2.id}" RETURN n1, rel, n2')

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

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        if id_type is None:
            if detailed:
                result = {
                    'triplets': {'simple': 0, 'hyper': 0, 'episodic': 0, 'time': 0},
                    'nodes': {'object': 0, 'hyper': 0, 'episodic': 0, 'time': 0}
                }

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

        if id_type == 'node':
            query = f'MATCH (n:{item_id.type.value}) WHERE n.str_id = "{item_id.id}" RETURN n'
        elif id_type == 'relation':
            query = f'MATCH (n1)-[rel:{item_id.type.value}]-(n2) WHERE rel.str_id = "{item_id.id}" RETURN rel'
        elif id_type == 'triplet':
            query = f'MATCH (n1)-[rel]-(n2) WHERE rel.t_id = "{item_id}" RETURN rel'
        else:
            raise ValueError

        output = self.execute_query(query)
        return len(output) > 0

    def clear(self) -> None:
        self.execute_query("MATCH (n)-[rel]->() DELETE n,rel")
        self.execute_query("MATCH (n) DELETE n")
