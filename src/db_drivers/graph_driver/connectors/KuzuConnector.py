from typing import List, Dict
from collections import defaultdict
import kuzu
import shutil
import gc
from time import time
import hashlib
import json
import joblib
import os

from ....utils.errors import ReturnInfo
from ....utils.data_structs import Node

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils import Triplet, NodeType

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig(
    params={'path': '../../kuzu_volume', 'buffer_pool_size': 1024**3}
)

class KuzuConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: GraphDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> ReturnInfo:
        load_path = f'{self.config.params['path']}/{self.config.db_info['db']}'

        if not os.path.exists(load_path):
            print(f"warning: graph-dump '{load_path}' doesnt exists. creating empty graph-store")

        self.db = kuzu.Database(load_path, buffer_pool_size=self.config.params['buffer_pool_size'])
        self.conn = kuzu.Connection(self.db)

        if self.config.need_to_clear:
            self.clear()

    def close_connection(self) -> ReturnInfo:
        self.conn.close()
        self.db.close()

    def is_open(self) -> bool:
        return not self.conn.is_closed

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
        query_props['str_id'] = json.dumps(node.id, ensure_ascii=False)

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

    def create(self, triplets: List[object], creation_info: Dict = dict()) -> ReturnInfo:
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
                self.conn.execute(insert_subj_query)
            if cur_info is None or cur_info['e_node']:
                insert_obj_query = self.create_node_query(triplet.end_node)
                self.conn.execute(insert_obj_query)

            insert_rel_query = self.create_rel_query(triplet)
            self.conn.execute(insert_rel_query)

    def read(self, ids: List[str]) -> List[object]:
        # TODO
        pass

    def update(self, items: List[object]) -> ReturnInfo:
        # TODO
        pass

    def delete(self, ids: List[str]) -> ReturnInfo:
        # TODO
        pass

    def parse_query_output(self, output: List[object]) -> List[Triplet]:
        # TODO
        return output

    def get_adjecent_nodes(self, base_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        if type(base_node_id) is not str:
            raise ValueError

        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        raw_nodes = self.conn.execute(
            f'MATCH (a)-[r]-(b) WHERE a.str_id = "{base_node_id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b']['str_id'] for node in raw_nodes]
        return formated_nodes

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        formatted_triplets = []
        if subj_names:
            for subj_name in subj_names:
                output = self.conn.execute(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n1.name) = LOWER("{subj_name}") RETURN n1, rel, n2')
                formatted_triplets += self.parse_query_output(output)
        elif obj_names:
            for obj_name in obj_names:
                output = self.conn.execute(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n2.name) = LOWER("{obj_name}") RETURN n1, rel, n2')
                formatted_triplets += self.parse_query_output(output)
        else:
            output = self.conn.execute(
                f'MATCH (n1:object)-[rel]-(n2:{obj_type}) RETURN n1, rel, n2')
            formatted_triplets += self.parse_query_output(output)
        return formatted_triplets

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        if (type(node1_id) is not str) or (type(node2_id) is not str):
            raise ValueError
        if (not self.item_exist(node1_id, id_type='node')) or (not self.item_exist(node2_id, id_type='node')):
            raise ValueError

        output = self.conn.execute(
            f'MATCH (n1)-[rel]-(n2) WHERE n1.str_id = "{node1_id}" AND n2.str_id = "{node2_id}" RETURN n1, rel, n2')

        formatted_triplets = self.parse_query_output(output)
        return formatted_triplets

    def count_items(self) -> int:
        n_output = self.conn.execute("MATCH (a) RETURN count(a) as n_count")[0]
        r_output = self.conn.execute("MATCH (a)-[rel]->(b) RETURN count(rel) as r_count")[0]
        return {'triplets': r_output['r_count'], 'nodes': n_output['n_count']}

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

        output = self.conn.execute(query)
        return len(output) > 0

    def clear(self) -> None:
        self.conn.execute("MATCH (n)-[rel]->() DELETE n,rel")
        self.conn.execute("MATCH (n) DELETE n")
