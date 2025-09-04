from ..utils import TreeDBConnectionConfig, TreeNodeType

DEFAULT_NEO4JTREE_CONFIG = TreeDBConnectionConfig(
    host="localhost", port="7688", db_info={'db': 'testingtree', 'table': 'testingtree'},
    params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=False)

DEFAULT_KUZUTREE_CONFIG = TreeDBConnectionConfig(
    params={'path': '../../kuzu_volume', 'buffer_pool_size': 1024**3,
            'schema': [
                "CREATE NODE TABLE IF NOT EXISTS leaf (id SERIAL, external_id STRING, str_id STRING, text STRING, props MAP(STRING, STRING), PRIMARY KEY(id));",
                "CREATE NODE TABLE IF NOT EXISTS summarized (id SERIAL, external_id STRING, text STRING, props MAP(STRING, STRING), PRIMARY KEY(id));",
                "CREATE NODE TABLE IF NOT EXISTS root (id SERIAL, external_id STRING, text STRING, props MAP(STRING, STRING), PRIMARY KEY(id));"
            ],
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
