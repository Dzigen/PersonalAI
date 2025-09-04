from typing import List, Dict
import kuzu
import json
import os

from .configs import DEFAULT_KUZUTREE_CONFIG
from ..utils import AbstractTreeDatabaseConnection, TreeDBConnectionConfig, \
    TreeNode, TreeNodeType, TreeIdType

class KuzuTreeConnector(AbstractTreeDatabaseConnection):

    def __init__(self, config: TreeDBConnectionConfig = DEFAULT_KUZUTREE_CONFIG):
        self.config = config

    def open_connection(self) -> None:
        load_path = f"{self.config.params['path']}/{self.config.db_info['db']}"

        if not os.path.exists(load_path):
            print(f"warning: graph-dump '{load_path}' doesnt exists. creating empty graph-store")

        self.db = kuzu.Database(load_path, buffer_pool_size=self.config.params['buffer_pool_size'])
        self.conn = kuzu.Connection(self.db)

        for schema_statement in self.config.params['schema']:
            self.conn.execute(schema_statement)

        # Creating indexes
        self.conn.execute("CREATE INDEX extid_leaf_node IF NOT EXISTS FOR (n:leaf) ON n.external_id;")
        self.conn.execute("CREATE INDEX strid_leaf_node IF NOT EXISTS FOR (n:leaf) ON n.str_id;")
        self.conn.execute("CREATE INDEX extid_summ_node IF NOT EXISTS FOR (n:summarized) ON n.external_id;")
        self.conn.execute("CREATE INDEX extid_root_node IF NOT EXISTS FOR (n:root) ON n.external_id;")

        # Добавляем корневую вершину
        if self.count_items()['root'] < 1:
            self.conn.execute("CREATE (n:root {" + 'external_id: "' + self.root_node_id + '", depth: 0});')

        if self.config.need_to_clear:
            self.clear()

        self.config.params['table_type_map']['nodes']['inverse'] = {v: k for k,v in self.config.params['table_type_map']['nodes']['forward'].items()}


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
        summarized_wo_childs = self.conn.execute("MATCH (parent:summarized) WHERE COUNT { (parent)-[rel]->() } < 1 RETURN parent;")
        assert len(summarized_wo_childs) < 1
        # нет leaf-вершин c детьми
        leafs_with_childs = self.conn.execute("MATCH (parent:leaf) WHERE COUNT { (parent)-[rel]->() } > 1 RETURN parent;")
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
                continue
            prop_keys.append(prop_name.replace(" ", "_"))
            prop_values.append(prop_value)


        fields['text'] = json.dumps(node.text, ensure_ascii=False)
        fields['external_id'] = json.dumps(node.id, ensure_ascii=False)
        fields['props'] = f"map({prop_keys},{prop_values})"
        str_fields = ", ".join([f"{k}: {v}" for k, v in fields.items()])

        node_t = self.config.params['table_type_map']['nodes']['forward'][node.type.value]
        query = f"CREATE (n:{node_t} " + "{" + str_fields + "}) RETURN elementId(n) as node_id"
        return query

    def create_rel_query(self, parent_id: str, child_id: str) -> str:
        query = f'MATCH (parent), (child) WHERE parent.external_id = "{parent_id}" AND child.external_id = "{child_id}" '
        query += f'CREATE (parent)-[rel]->(child) '
        query += 'RETURN elementId(rel) as rel_id;'
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
        rel_query = self.create_rel_query(parent_id, new_node.id)
        self.conn.execute(rel_query)

    def read(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> List[TreeNode]:
        if type(ids_type) is not TreeIdType:
            raise ValueError
        for id in ids:
            if type(id) is not str:
                raise ValueError

        formated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', ids))) + ']'
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
        for cur_old_item in old_items:
            cur_new_item = new_items_map[cur_old_item.id]

            if cur_old_item.type == TreeNodeType.root:
                assert cur_new_item.type == TreeNodeType.root

            # Получем идентификаторы вершин, с которыми смежна обновляемая вершина
            ## parent-вершины
            output = self.conn.execute(f'MATCH (parent)-[rel]->(child) WHERE child.external_id = "{cur_old_item.id}" RETURN parent.external_id as p_eid;')
            parent_ids = list(output.get_as_df()['p_eid'])
            if cur_old_item.type != TreeNodeType.root:
                assert parent_ids == 1
            ## child-вершины
            output = self.conn.execute(f'MATCH (parent)-[rel]->(child) WHERE parent.external_id = "{cur_old_item.id}" RETURN child.external_id as c_eid;')
            child_ids = list(output.get_as_df()['c_eid'])

            # Удаляем все инцидентные связи у обновляемой вершины
            self.conn.execute(f'MATCH (parent)-[rel]->(child) WHERE child.external_id = "{cur_old_item.id}" DELETE rel;')
            output = self.conn.execute(f'MATCH (parent)-[rel]->(child) WHERE parent.external_id = "{cur_old_item.id}" DELETE rel;')
            # Удаляем старую версию обновляемой вершины
            self.conn.execute(f'MATCH (n) WHERE n.external_id = "{cur_old_item.id}" DELETE n;')

            # Добавляем обновлённую версию вершины
            node_query = self.create_node_query(cur_new_item)
            self.conn.execute(node_query)

            # К новой версии вершины добавляем все связи, которые были у старой версии
            ## parent-связи
            pformated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', parent_ids))) + ']'
            query = f'MATCH (parent), (child) WHERE child.external_id = "{cur_new_item.id}" AND ANY(id IN {pformated_ids} WHERE n.external_id = id) '
            query += f'CREATE (parent)-[rel]->(child) '
            query += 'RETURN elementId(rel) as rel_id;'
            self.conn.execute(node_query)
            ## child-связи
            cformated_ids = '['+', '.join(list(map(lambda id: f'"{id}"', child_ids))) + ']'
            query = f'MATCH (parent), (child) WHERE parent.external_id = "{cur_new_item.id}" AND ANY(id IN {cformated_ids} WHERE n.external_id = id) '
            query += f'CREATE (parent)-[rel]->(child) '
            query += 'RETURN elementId(rel) as rel_id;'
            self.conn.execute(node_query)

    def delete(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> None:
        if type(ids_type) is not TreeIdType:
            raise ValueError
        for id in ids:
            if type(id) is not str:
                raise ValueError
            # Проверка: у удаляемой вершины не должно быть детей
            if self.item_exist(id, id_type=ids_type):
                cur_node = self.read([id], ids_type=ids_type)[0]
                childs_amount = len(self.get_child_nodes(cur_node.id))
                if childs_amount > 0:
                    raise ValueError

        for id in ids:
            self.conn.execute(f'MATCH (parent)-[rel]->(leaf) WHERE leaf.{ids_type.value} = "{id}" DELETE rel;')
            self.conn.execute(f'MATCH (leaf) WHERE leaf.{ids_type.value} = "{id}" DELETE leaf;')

    def count_items(self) -> Dict[str, int]:
        leafs_amount = self.conn.execute("MATCH (n:leaf) return COUNT(n) as l_amount;")[0]['l_amount']
        summarized_amount = self.conn.execute("MATCH (n:summarized) return COUNT(n) as s_amount;")[0]['s_amount']
        root_amount = self.conn.execute("MATCH (n:root) return COUNT(n) as r_amount;")[0]['r_amount']

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

        output = self.conn.execute(query)
        return len(output) > 0

    def is_node_valid(self, node: TreeNode) -> bool:
        if type(node.type) is not TreeNodeType:
            return False
        if type(node.id) is not str:
            return False
        if type(node.text) is not str:
            return False
        if type(node.props) is not dict:
            return False

        # все значения по ключам в props-поле
        # должны иметь str-тип
        for k in node.props.keys():
            if type(k) is not str:
                return False
        # extrtnal_id-ключ зарезервирован
        if 'external_id' in node.props:
            return False
        # у веришин leaf-типа обязательное должно присутствовать str_id-значение
        if node.type == TreeNodeType.leaf and 'str_id' not in node.props:
            raise False

        return True

    def formate_nodes_output(self, output: object) -> List[TreeNode]:
        formated_nodes = []
        output = output.get_as_df()
        nodes_count = len(output['n'])
        for i in range(nodes_count):
            raw_node = output['n'][i]
            node_type = self.config.params['table_type_map']['nodes']['inverse'][raw_node['_label']]

            cur_f_node = TreeNode(
                id=raw_node['external_id'], text=raw_node['text'],
                type=node_type, props=dict(raw_node['prop']))
            if cur_f_node.type == TreeNodeType.leaf:
                cur_f_node.props['str_id'] = raw_node['str_id']

            formated_nodes.append(cur_f_node)
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

        raw_nodes = self.conn.execute(f'MATCH (parent)-[rel]->(n) WHERE parent.{id_type.value} = "{id}" RETURN n;')
        formated_nodes = self.formate_nodes_output(raw_nodes)
        return formated_nodes

    def get_tree_maxdepth(self) -> int:
        return self.conn.execute("MATCH (n) RETURN MAX(n.depth) as max_depth;")[0]['max_depth']

    def clear(self) -> None:
        self.conn.execute("MATCH (n)-[rel]->() DELETE n,rel;")
        self.conn.execute("MATCH (n) DELETE n;")
        # Добавляем корневую вершину
        self.conn.execute("CREATE (n:root {" + 'external_id: "' + self.root_node_id + '", depth: 0});')
