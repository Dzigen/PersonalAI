from ..utils import GraphDBConnectionConfig
from ....utils.data_structs import NodeType, RelationType


DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig(
    params={
        'load_from_disk': False,
        'load_dump_name': None,
        'load_dump_dir': "./personalai_tmp/volumes/inmemory_graph",
        'save_on_disk': True, 'save_dump_dir': "./personalai_tmp/volumes/inmemory_graph",
    }
)

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig(
    params={
        'path': "./personalai_tmp/volumes/kuzu_graph", 'buffer_pool_size': 1024**3,
        'table_type_map': {
            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'}, },
            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
        }
    }
)

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(
    host='localhost', port=7687, params={'user': "neo4j", 'pwd': 'password'})
