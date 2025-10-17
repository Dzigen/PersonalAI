from ..utils import TreeDBConnectionConfig, TreeNodeType

DEFAULT_NEO4JTREE_CONFIG = TreeDBConnectionConfig(
    host="localhost", port="7680",
    params={'user': "neo4j", 'pwd': 'password'},
    need_to_clear=False)

DEFAULT_KUZUTREE_CONFIG = TreeDBConnectionConfig(
    params={'path': "./personalai_tmp/volumes/kuzu_tree", 'buffer_pool_size': 1024**3,
            'table_type_map': {
                'nodes': {
                    'forward': {
                        TreeNodeType.root.value: 'root',
                        TreeNodeType.leaf.value: 'leaf',
                        TreeNodeType.summarized.value: 'summarized'
                    }
                }
            }
            },
    need_to_clear=False
)
