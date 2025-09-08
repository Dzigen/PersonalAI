from typing import List, Dict
import kuzu
import json
import os
from itertools import groupby

from .configs import DEFAULT_KUZUTREE_CONFIG
from ..utils import AbstractTreeDatabaseConnection, TreeDBConnectionConfig, \
    TreeNode, TreeNodeType, TreeIdType, TREENODES_TYPES_MAP

class KuzuTreeConnector(AbstractTreeDatabaseConnection):

    def __init__(self, config: TreeDBConnectionConfig = DEFAULT_KUZUTREE_CONFIG):
        self.config = config

    def open_connection(self) -> None:
        load_path = f"{self.config.params['path']}/{self.config.db_info['db']}"

        if not os.path.exists(load_path):
            print(f"warning: graph-dump '{load_path}' doesnt exists. creating empty graph-store")

        self.db = kuzu.Database(load_path, buffer_pool_size=self.config.params['buffer_pool_size'])
        self.conn = kuzu.Connection(self.db)

        schema = [
            "CREATE NODE TABLE IF NOT EXISTS leaf (id SERIAL, external_id STRING, str_id STRING, text STRING, depth INT64, props MAP(STRING, STRING), PRIMARY KEY(id));",
            "CREATE NODE TABLE IF NOT EXISTS summarized (id SERIAL, external_id STRING, text STRING, depth INT64, descendants_num INT64, props MAP(STRING, STRING), PRIMARY KEY(id));",
            "CREATE NODE TABLE IF NOT EXISTS root (id SERIAL, external_id STRING, depth INT64, props MAP(STRING, STRING), PRIMARY KEY(id));",
            "CREATE REL TABLE GROUP IF NOT EXISTS relation (FROM root TO summarized, FROM root TO leaf, FROM summarized TO summarized, FROM summarized TO leaf);"]
        for schema_statement in schema:
            self.conn.execute(schema_statement)

        # Creating indexes
        # if self.config.create_index:
        #     cquery_statements = [
        #         "CREATE INDEX extid_leaf_node IF NOT EXISTS FOR (n:leaf) ON n.external_id;",
        #         "CREATE INDEX strid_leaf_node IF NOT EXISTS FOR (n:leaf) ON n.str_id;",
        #         "CREATE INDEX extid_summ_node IF NOT EXISTS FOR (n:summarized) ON n.external_id;",
        #         "CREATE INDEX extid_root_node IF NOT EXISTS FOR (n:root) ON n.external_id;"]
        #     for cqueru in cquery_statements:
        #         self.execute_query(cqueru)

        print("before: ",self.count_items())

        # Добавляем корневую вершину
        if self.count_items()['root'] < 1:
            self.conn.execute("CREATE (n:root {" + 'external_id: "' + self.root_node_id + '", depth: 0});')

        if self.config.need_to_clear:
            self.clear()

        self.config.params['table_type_map']['nodes']['inverse'] = {v: k for k,v in self.config.params['table_type_map']['nodes']['forward'].items()}

        print("after: ",self.count_items())


    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> None:
        self.conn.close()
        self.db.close()

    def __del__(self):
        self.close_connection()

    def check_consistency(self) -> None:
        # У всех leaf-вершин есть str_id-поле
        leafs_wo_strid = self.conn.execute("MATCH (n:leaf) WHERE n.str_id IS NULL RETURN COUNT(n) as badleafs;")[0]['badleafs']
        assert leafs_wo_strid < 1

        # количество компонент связности равно 1
        #components_amount = self.conn.execute(f"CALL gds.wcc.stats('{self.config.db_info['db']}') YIELD componentCount")[0]['componentCount']
        #assert components_amount < 2

        # нет summarized-вершин без детей
        summarized_wo_childs = self.conn.execute("MATCH (parent:summarized) WHERE COUNT { (parent)-[rel:relation]->() } < 1 RETURN parent;")
        assert len(summarized_wo_childs) < 1
        # нет leaf-вершин c детьми
        leafs_with_childs = self.conn.execute("MATCH (parent:leaf) WHERE COUNT { (parent)-[rel:relation]->() } > 1 RETURN parent;")
        assert len(leafs_with_childs) < 1

        nodes_count = self.count_items()
        # есть 1 root-вершина
        assert nodes_count['root'] < 2 and nodes_count['root'] > 0
        # summarized-вершин <= leaf-вершин
        assert nodes_count['summarized'] <= nodes_count['leaf']

    def create_node_query(self, node: TreeNode) -> str:
        fields = {}
        prop_keys, prop_values = [], []
        for prop_name, prop_value in node.props.items():
            if prop_name == 'str_id' and node.type == TreeNodeType.leaf:
                fields['str_id'] = json.dumps(node.props['str_id'], ensure_ascii=False)
            elif prop_name == 'depth':
                fields['depth'] = node.props['depth']
            elif prop_name == 'descendants_num':
                fields['descendants_num'] = node.props['descendants_num']
            else:
                prop_keys.append(prop_name.replace(" ", "_"))
                prop_values.append(prop_value)

        fields['text'] = json.dumps(node.text, ensure_ascii=False)
        fields['external_id'] = json.dumps(node.id, ensure_ascii=False)
        fields['props'] = f"map({prop_keys},{prop_values})"
        str_fields = ", ".join([f"{k}: {v}" for k, v in fields.items()])

        node_t = self.config.params['table_type_map']['nodes']['forward'][node.type.value]
        query = f"CREATE (n:{node_t} " + "{" + str_fields + "});"
        return query

    def create_rel_query(self, parent_id: str, parent_label: str, child_id: str, child_label: str) -> str:
        query = f'MATCH (parent:{parent_label}), (child:{child_label}) WHERE parent.external_id = "{parent_id}" AND child.external_id = "{child_id}" '
        query += f'CREATE (parent)-[rel:relation]->(child);'
        return query

    def create(self, parent_id: str, new_node: TreeNode) -> None:
        # Подвешиваем новую вершину к уже существующей
        # parent_id должен быть валидным и сущесутвовать
        # У new_node должен быть валидный id, type, text, не должно храниться зарезервированных полей
        # если вершина с таким id уже существует, то вызыватеся исключение

        if type(parent_id) is not str:
            raise ValueError
        if not self.is_node_valid(new_node):
            raise ValueError
        if not self.item_exist(parent_id, TreeIdType.external):
            raise ValueError
        if self.item_exist(new_node.id, TreeIdType.external):
            raise ValueError

        # добавляем новую вершину
        node_query = self.create_node_query(new_node)
        self.conn.execute(node_query)

        # добавляем связь между parent- и её новой child-вершиной
        parent_type = self.conn.execute(f'MATCH (n) WHERE n.external_id = "{parent_id}" RETURN LABEL(n) AS nodeType').get_as_df()['nodeType'][0]
        rel_query = self.create_rel_query(parent_id, parent_type, new_node.id, new_node.type.value)
        self.conn.execute(rel_query)

    def read(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> List[TreeNode]:
        if type(ids_type) is not TreeIdType:
            raise ValueError
        for id in ids:
            if type(id) is not str:
                raise ValueError

        formated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', ids))) + ']'
        print(formated_ids)
        query = f"MATCH (n) WHERE any(id IN {formated_ids} WHERE n.{ids_type.value} = id) RETURN n;"
        raw_nodes = self.conn.execute(query)

        # Приводим информацию о полученных вершинах к нужному формату
        formated_nodes = self.formate_nodes_output(raw_nodes)

        return formated_nodes

    def update(self, items: List[TreeNode]) -> None:
        new_items_map = dict()
        for item in items:
            if not self.is_node_valid(item):
                raise ValueError
            if not self.item_exist(item.id):
                raise ValueError
            new_items_map[item.id] = item

        old_items = self.read(list(new_items_map.keys()))
        print("old nodes:",old_items)
        print("new nodes:", new_items_map)
        for cur_old_item in old_items:
            cur_new_item = new_items_map[cur_old_item.id]
            cur_nnode_type = self.config.params['table_type_map']['nodes']['forward'][cur_new_item.type.value]
            print("cur node:", cur_new_item)

            if cur_old_item.type == TreeNodeType.root:
                assert cur_new_item.type == TreeNodeType.root

            # Получем идентификаторы вершин, с которыми смежна обновляемая вершина
            ## parent-вершины
            output = self.conn.execute(f'MATCH (parent)-[rel:relation]->(child) WHERE child.external_id = "{cur_old_item.id}" RETURN parent.external_id as p_eid, LABEL(parent) as p_label;').get_as_df()
            pnodes_info = [(output['p_eid'][i], output['p_label'][i]) for i in range(len(output['p_eid']))]
            pnodes_info.sort(key=lambda x: x[1])
            grouped_pnodes = {k: [item[0] for item in g] for k, g in groupby(pnodes_info, key=lambda x: x[1])}
            print("parent_ids:", pnodes_info)
            if cur_old_item.type != TreeNodeType.root:
                assert len(pnodes_info) == 1
            ## child-вершины
            output = self.conn.execute(f'MATCH (parent)-[rel:relation]->(child) WHERE parent.external_id = "{cur_old_item.id}" RETURN child.external_id as c_eid, LABEL(child) as c_label;').get_as_df()
            cnodes_info = [(output['c_eid'][i], output['c_label'][i]) for i in range(len(output['c_eid']))]
            cnodes_info.sort(key=lambda x: x[1])
            grouped_cnodes = {k: [item[0] for item in g] for k, g in groupby(cnodes_info, key=lambda x: x[1])}
            print("child_ids:", cnodes_info)

            # Удаляем все инцидентные связи у обновляемой вершины
            self.conn.execute(f'MATCH (parent)-[rel:relation]->(child) WHERE child.external_id = "{cur_old_item.id}" DELETE rel;')
            self.conn.execute(f'MATCH (parent)-[rel:relation]->(child) WHERE parent.external_id = "{cur_old_item.id}" DELETE rel;')
            # Удаляем старую версию обновляемой вершины
            self.conn.execute(f'MATCH (n) WHERE n.external_id = "{cur_old_item.id}" DELETE n;')

            # Добавляем обновлённую версию вершины
            node_query = self.create_node_query(cur_new_item)
            self.conn.execute(node_query)

            # К новой версии вершины добавляем все связи, которые были у старой версии
            ## parent-связи
            for p_type, p_ids in grouped_pnodes.items():
                pformated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', p_ids))) + ']'
                prel_query = f'MATCH (parent:{p_type}), (child:{cur_nnode_type}) WHERE child.external_id = "{cur_new_item.id}" AND ANY(id IN {pformated_ids} WHERE parent.external_id = id) '
                prel_query += f'CREATE (parent)-[rel:relation]->(child);'
                self.conn.execute(prel_query)
            ## child-связи
            for c_type, c_ids in grouped_cnodes.items():
                cformated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', c_ids))) + ']'
                crel_query = f'MATCH (parent:{cur_nnode_type}), (child:{c_type}) WHERE parent.external_id = "{cur_new_item.id}" AND ANY(id IN {cformated_ids} WHERE child.external_id = id) '
                crel_query += f'CREATE (parent)-[rel:relation]->(child);'
                self.conn.execute(crel_query)

    def delete(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> None:
        if type(ids_type) is not TreeIdType:
            raise ValueError
        for id in ids:
            if type(id) is not str:
                raise ValueError
            # Проверка: у удаляемой вершины не должно быть детей
            if self.item_exist(id, id_type=ids_type):
                childs_amount = len(self.get_child_nodes(id, id_type=ids_type))
                if childs_amount > 0:
                    raise ValueError

        for id in ids:
            self.conn.execute(f'MATCH (parent)-[rel:relation]->(leaf) WHERE leaf.{ids_type.value} = "{id}" DELETE rel;')
            self.conn.execute(f'MATCH (leaf) WHERE leaf.{ids_type.value} = "{id}" DELETE leaf;')

    def count_items(self) -> Dict[str, int]:
        leafs_amount = self.conn.execute("MATCH (n:leaf) return COUNT(n) as l_amount;").get_as_df()['l_amount'][0]
        summarized_amount = self.conn.execute("MATCH (n:summarized) return COUNT(n) as s_amount;").get_as_df()['s_amount'][0]
        root_amount = self.conn.execute("MATCH (n:root) return COUNT(n) as r_amount;").get_as_df()['r_amount'][0]

        return {'leaf': leafs_amount, 'summarized': summarized_amount, 'root': root_amount}

    def item_exist(self, id: str, id_type: str = TreeIdType.external) -> bool:
        if type(id) is not str:
            raise ValueError

        if id_type == TreeIdType.external:
            query = f'MATCH (n) WHERE n.external_id = "{id}" RETURN n;'
        elif id_type == TreeIdType.str:
            query = f'MATCH (n) WHERE n.str_id = "{id}" RETURN n;'
        else:
            raise ValueError

        raw_output = self.conn.execute(query)
        existed_items = raw_output.get_as_df()['n']
        return len(existed_items) > 0

    def is_node_valid(self, node: TreeNode) -> bool:
        if type(node.type) is not TreeNodeType:
            return False
        if type(node.id) is not str:
            return False
        if type(node.text) is not str:
            return False
        if type(node.props) is not dict:
            return False

        # if node.type == TreeNodeType.summarized and 'descendants_num' not in node.props:
        #     return False
        # if node.type != TreeNodeType.summarized and 'descendants_num' in node.props:
        #     return False
        if 'depth' not in node.props:
            return False

        # все ключи и значения по ключам в props-поле
        # должны иметь str-тип
        for k,v in node.props.items():
            if (node.type == TreeNodeType.summarized and k == 'descendants_num') or k == 'depth':
                if type(v) is not int:
                    raise ValueError
            else:
                if type(v) is not str:
                    return False

        # extrtnal_id-ключ зарезервирован
        if 'external_id' in node.props:
            return False
        # у веришин leaf-типа обязательное должно присутствовать str_id-значение
        if node.type == TreeNodeType.leaf and 'str_id' not in node.props:
            return False

        return True

    def formate_nodes_output(self, output: object) -> List[TreeNode]:
        formated_nodes = []
        output = output.get_as_df()
        nodes_count = len(output['n'])
        for i in range(nodes_count):
            raw_node = output['n'][i]
            node_type = TREENODES_TYPES_MAP[self.config.params['table_type_map']['nodes']['inverse'][raw_node['_label']]]
            print(node_type, raw_node)

            cur_f_node = TreeNode(
                id=raw_node['external_id'], text=raw_node['text'],
                type=node_type, props=dict(raw_node['props']))
            if cur_f_node.type == TreeNodeType.leaf:
                cur_f_node.props['str_id'] = raw_node['str_id']
            elif cur_f_node.type == TreeNodeType.summarized and raw_node['descendants_num'] is not None:
                cur_f_node.props['descendants_num'] = raw_node['descendants_num']
            cur_f_node.props['depth'] = raw_node['depth']

            formated_nodes.append(cur_f_node)
        print("HERE")
        return formated_nodes

    def get_leaf_descendants(self, id: str, id_type: TreeIdType = TreeIdType.external) -> List[TreeNode]:
        if type(id) is not str:
            raise ValueError
        if type(id_type) is not TreeIdType:
            raise ValueError
        if not self.item_exist(id, id_type=id_type):
            raise ValueError

        raw_output = self.conn.execute(f'MATCH (ancestor)-[:relation*0..]->(n:leaf) WHERE ancestor.{id_type.value} = "{id}" RETURN n;')
        leaf_nodes = self.formate_nodes_output(raw_output)
        return leaf_nodes

    def get_child_nodes(self, parent_id: str, id_type: TreeIdType = TreeIdType.external) -> List[TreeNode]:
        if type(parent_id) is not str:
            raise ValueError
        if not self.item_exist(parent_id, id_type=id_type):
            raise ValueError

        raw_nodes = self.conn.execute(f'MATCH (parent)-[rel:relation]->(n) WHERE parent.{id_type.value} = "{parent_id}" RETURN n;')
        formated_nodes = self.formate_nodes_output(raw_nodes)
        return formated_nodes

    def get_tree_maxdepth(self) -> int:
        raw_output = self.conn.execute("MATCH (n) RETURN MAX(n.depth) as max_depth;")
        max_depth = int(raw_output.get_as_df()['max_depth'][0])
        return max_depth

    def clear(self) -> None:
        self.conn.execute("MATCH (n1)-[rel]->(n2) DELETE rel;")
        self.conn.execute("MATCH (n) DELETE n;")
        # Добавляем корневую вершину
        self.conn.execute("CREATE (n:root {" + 'external_id: "' + self.root_node_id + '", depth: 0});')
