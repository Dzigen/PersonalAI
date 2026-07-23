from falkordb import FalkorDB, Node, QueryResult, Edge
from typing import List, Dict, Union
import redis
import json

from .configs import DEFAULT_FALKORDB_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.data_structs import Triplet, Node, TripletCreator, NodeCreator, \
    NodeType, RelationCreator, RelationType, NODES_TYPES_MAP, RELATIONS_TYPES_MAP, \
    NodeInfo, RelationInfo, TripletInfo

# Useful Material: FalkorDB -- Ultra-fast, Multi-tenant Graph Database
# https://github.com/FalkorDB/FalkorDB


class FalkorDBGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_FALKORDB_CONFIG):
        if isinstance(config, dict):
            config = GraphDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: GraphDBConnectionConfig = config

    def open_connection(self) -> None:
        self.db = FalkorDB(host=self.config.host, port=self.config.port)
        self.graph = self.db.select_graph(f"{self.config.db_info['db']}{self.config.db_info['table']}")

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
                self.graph.query(cqueru)

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> None:
        # TODO
        raise NotImplementedError

    def close_connection(self) -> None:
        # TODO
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
            str_props + "}) RETURN ID(n) as node_id"
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
        query += 'RETURN ID(rel) as rel_id'
        return query

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if not isinstance(triplet.id, str):
                raise ValueError(f"* bad triplet: {triplet}\n* triplets: {triplets}")
        unique_ids = set(map(lambda triplet: triplet.id, triplets))
        if len(triplets) != len(unique_ids):
            raise ValueError(f"triplets: {triplets}")

        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)
            if cur_info is None or cur_info['s_node']:
                insert_subj_query = self.create_node_query(triplet.start_node)
                self.graph.query(insert_subj_query)
            if cur_info is None or cur_info['e_node']:
                insert_obj_query = self.create_node_query(triplet.end_node)
                self.graph.query(insert_obj_query)

            insert_rel_query = self.create_rel_query(triplet)
            self.graph.query(insert_rel_query)

    def read(self, ids: List[str]) -> List[Triplet]:
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError(f"* bad id: {t_id}\n* ids: {ids}")

        str_ids = '[' + ', '.join(list(map(lambda id: f'"{id}"', ids))) + ']'
        query = f"MATCH (n1)-[rel]->(n2) WHERE any(id IN {str_ids} WHERE rel.t_id = id) RETURN n1, rel, n2"
        raw_output = self.graph.ro_query(query)
        triplets = self.parse_query_triplets_output(raw_output)
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        for t_id in ids:
            if not isinstance(t_id, str):
                raise ValueError(f"* bad id: {t_id}\n* ids: {ids}")

        for i, t_id in enumerate(ids):
            cur_info = delete_info.get(i, None)
            nodes_to_delete = []

            if cur_info is None or cur_info['s_node']:
                nodes_to_delete.append('sn')

            if cur_info is None or cur_info['e_node']:
                nodes_to_delete.append('en')

            output = self.graph.query(
                f'MATCH (s_node)-[rel]->(e_node) WHERE rel.t_id = "{t_id}" DELETE rel \
                    RETURN ID(s_node) as sn_id, labels(s_node) as sn_labels, ID(e_node) as en_id, labels(e_node) as en_labels').result_set
            # print(output)
            if len(output) < 1:
                continue

            assert len(output) == 1

            npos_to_idx_map = {
                'sn_id': 0, 'sn_labels': 1,
                'en_id': 2, 'en_labels': 3
            }

            if len(nodes_to_delete) > 0:
                where_statement = []
                for n_name in nodes_to_delete:
                    node_id = output[0][npos_to_idx_map[f"{n_name}_id"]]
                    node_type = output[0][npos_to_idx_map[f"{n_name}_labels"]][0]

                    where_statement.append(f'(ID(n) = {node_id} and n:{node_type})')
                where_statement = ' or '.join(where_statement)
                self.graph.query(f'MATCH (n) WHERE {where_statement} DELETE n')

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        if type(object_type) not in [RelationType, NodeType]:
            raise ValueError(f"object_type: {object_type}")

        if not isinstance(name, str):
            raise ValueError(f"name: {name}")

        if len(name) < 1:
            raise ValueError(f"name: {name}")

        dump_name = json.dumps(name, ensure_ascii=False)
        if object == 'relation':
            output = self.graph.ro_query(
                f'MATCH (n1)-[rel:{object_type.value}]->(n2) WHERE rel.name = {dump_name} RETURN n1,rel,n2;')
            formated_output = self.parse_query_triplets_output(output)
        elif object == 'node':
            output = self.graph.ro_query(
                f'MATCH (n:{object_type.value}) WHERE n.name = {dump_name} RETURN n;')
            formated_output = self.parse_query_nodes_output(output)
        else:
            raise ValueError(f"object: {object}")

        return formated_output

    def get_adjacent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time]) -> List[NodeInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        raw_nodes = self.graph.ro_query(
            f'MATCH (a:{base_node.type.value})-[r]-(b) WHERE a.str_id = "{base_node.id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(b)) RETURN b')
        formated_nodes = [NodeInfo(id=node[0].properties['str_id'], type=NODES_TYPES_MAP[list(node[0].labels)[0]]) for node in raw_nodes.result_set]
        return formated_nodes

    def get_incident_triples(self, base_node: NodeInfo,
                             accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time],
                             accepted_r_types: Union[List[RelationType], None] = None) \
            -> List[TripletInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        str_accepted_nodes = ', '.join(list(map(lambda tpe: f'"{tpe.value}"', accepted_n_types)))

        str_accepted_relations = ""
        if accepted_r_types is not None:
            str_accepted_relations = ":" + '|'.join(list(map(lambda tpe: tpe.value, accepted_r_types)))

        output = self.graph.ro_query(
            f'MATCH (n1:{base_node.type.value})-[rel{str_accepted_relations}]-(n2) WHERE n1.str_id = "{base_node.id}" AND ANY(lbl in [{str_accepted_nodes}] where lbl in labels(n2)) RETURN n1,rel,n2')
        formated_output = self.parse_query_triplets_output(output)
        triples_info = [triple.get_info() for triple in formated_output]
        return triples_info

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")
        if not isinstance(id_type, str):
            raise ValueError(f"id_type: {id_type}")

        if id_type == 'triplet':
            str_return_info = 'r.t_id as t_id'
        elif id_type == 'relation':
            str_return_info = 'r.str_id as r_id'
        elif id_type == 'both':
            str_return_info = 'r.t_id as t_id, r.str_id as r_id'
        else:
            raise ValueError(f"id_type: {id_type}")

        raw_rels = self.graph.ro_query(
            f'MATCH (a:{node1.type.value})-[r]-(b:{node2.type.value}) WHERE a.str_id = "{node1.id}" AND b.str_id = "{node2.id}" RETURN {str_return_info};')

        formated_info = []
        for raw_rel in raw_rels.result_set:
            # print(raw_rel)
            tmp_info = dict()
            if id_type == 'both':
                tmp_info['t_id'] = raw_rel[0]
                tmp_info['r_id'] = raw_rel[1]
            elif id_type == 'triplet':
                tmp_info['t_id'] = raw_rel[0]
            elif id_type == 'relation':
                tmp_info['r_id'] = raw_rel[0]
            else:
                raise ValueError(f"id_type: {id_type}")

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

    def parse_query_nodes_output(self, output: QueryResult) -> List[Node]:
        formated_nodes = []
        output = output.result_set
        for raw_node in output:

            n = raw_node[0]

            node = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(n.labels)[0]],
                name=n.properties['name'], prop=n.properties, add_stringified_node=False)
            del node.prop['name']

            formated_nodes.append(node)
        return formated_nodes

    def parse_query_triplets_output(self, output: QueryResult) -> List[Triplet]:
        formated_triplets = []
        output = output.result_set
        for raw_triplet in output:
            # print(raw_triplet)

            n1: Node = raw_triplet[0]
            rel: Edge = raw_triplet[1]
            n2: Node = raw_triplet[2]

            node1 = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(n1.labels)[0]],
                name=n1.properties['name'], prop=n1.properties, add_stringified_node=False)
            del node1.prop['name']

            node2 = NodeCreator.create(
                n_type=NODES_TYPES_MAP[list(n2.labels)[0]],
                name=n2.properties['name'], prop=n2.properties, add_stringified_node=False)
            del node2.prop['name']

            relation = RelationCreator.create(
                r_type=RELATIONS_TYPES_MAP[rel.relation],
                name=rel.properties['name'], prop=rel.properties)
            del relation.prop['name']

            start_node_id = rel.src_node
            if start_node_id == n1.id:
                start_node, end_node = (node1, node2)
            elif start_node_id == n2.id:
                start_node, end_node = (node2, node1)
            else:
                raise ValueError(f"raw_triplet: {raw_triplet}")

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
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")
        if (not self.item_exist(node1, 'node')) or (not self.item_exist(node2, 'node')):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")

        output = self.graph.ro_query(
            f'MATCH (n1:{node1.type.value})-[rel]-(n2:{node2.type.value}) WHERE n1.str_id = "{node1.id}" AND n2.str_id = "{node2.id}" RETURN n1, rel, n2')

        formated_triplets = self.parse_query_triplets_output(output)
        return formated_triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        formated_triplets = []
        if subj_names:
            for subj_name in subj_names:
                subj_dump = json.dumps(subj_name, ensure_ascii=False)
                output = self.graph.ro_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n1.name) = LOWER({subj_dump}) RETURN n1, rel, n2')
                formated_triplets += self.parse_query_triplets_output(output)
        elif obj_names:
            for obj_name in obj_names:
                obj_dump = json.dumps(obj_name, ensure_ascii=False)
                output = self.graph.ro_query(
                    f'MATCH (n1:object)-[rel]-(n2:{obj_type}) WHERE LOWER(n2.name) = LOWER({obj_dump}) RETURN n1, rel, n2')
                formated_triplets += self.parse_query_triplets_output(output)
        else:
            output = self.graph.ro_query(
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

                try:
                    n_output = self.graph.ro_query(
                        "MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS nodeCount").result_set
                    r_output = self.graph.ro_query(
                        "MATCH (a)-[rel]->(b) UNWIND type(rel) AS rel_type RETURN rel_type, count(rel) AS relCount").result_set

                    result['triplets'].update({item[0]: int(item[1]) for item in r_output})
                    result['nodes'].update({item[0]: int(item[1]) for item in n_output})

                # костыль: если граф только создан (пустой),
                # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
                except redis.exceptions.ResponseError:
                    pass

            else:
                try:
                    n_output = self.graph.ro_query("MATCH (a) RETURN COUNT(a) as n_count").result_set[0]
                    r_output = self.graph.ro_query("MATCH (a)-[rel]->(b) RETURN COUNT(rel) as r_count").result_set[0]
                    result = {'triplets': r_output[0], 'nodes': n_output[0]}
                # костыль: если граф только создан (пустой),
                # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
                except redis.exceptions.ResponseError:
                    result = {'triplets': 0, 'nodes': 0}

        elif id_type == 'node':
            try:
                n_output = self.graph.ro_query(
                    f'MATCH (a:{item_id.type.value}) WHERE a.str_id = "{item_id.id}" RETURN COUNT(a) as n_count').result_set[0]
                result = n_output[0]
            # костыль: если граф только создан (пустой),
            # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
            except redis.exceptions.ResponseError:
                result = 0

        elif id_type == 'relation':
            try:
                r_output = self.graph.ro_query(
                    f'MATCH (a)-[rel:{item_id.type.value}]->(b) WHERE rel.str_id = "{item_id.id}" RETURN COUNT(rel) as r_count').result_set[0]
                result = r_output[0]
            # костыль: если граф только создан (пустой),
            # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
            except redis.exceptions.ResponseError:
                result = 0

        elif id_type == 'triplet':
            try:
                r_output = self.graph.ro_query(f'MATCH (a)-[rel]->(b) WHERE rel.t_id = "{item_id}" RETURN COUNT(rel) as r_count').result_set[0]
                result = r_output[0]
            # костыль: если граф только создан (пустой),
            # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
            except redis.exceptions.ResponseError:
                result = 0
        else:
            raise ValueError(f"id_type: {id_type}")

        return result

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        if not isinstance(item_id, str):
            if type(item_id) in [NodeInfo, RelationInfo]:
                if not isinstance(item_id.id, str):
                    raise ValueError(f"item_id: {item_id}")
            else:
                raise ValueError(f"item_id: {item_id}")

        if id_type == 'node':
            query = f'MATCH (n:{item_id.type.value}) WHERE n.str_id = "{item_id.id}" RETURN n'
        elif id_type == 'relation':
            query = f'MATCH (n1)-[rel:{item_id.type.value}]-(n2) WHERE rel.str_id = "{item_id.id}" RETURN rel'
        elif id_type == 'triplet':
            query = f'MATCH (n1)-[rel]-(n2) WHERE rel.t_id = "{item_id}" RETURN rel'
        else:
            raise ValueError(f"id_type: {id_type}")

        try:
            output = self.graph.ro_query(query).result_set
        # костыль: если граф только создан (пустой),
        # то при отправке MATCH-запросов возникает ошибка - "redis.exceptions.ResponseError: Invalid graph operation on empty key"
        except redis.exceptions.ResponseError:
            output = []

        return len(output) > 0

    def clear(self) -> None:
        self.graph.query("MATCH (n)-[rel]->() DELETE n,rel")
        self.graph.query("MATCH (n) DELETE n")
