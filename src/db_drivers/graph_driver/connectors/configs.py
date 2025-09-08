from ..utils import GraphDBConnectionConfig
from ....utils.data_structs import NodeType, RelationType


DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig()

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig(
    params={
        'path': '../tmp/kuzu_volume', 'buffer_pool_size': 1024**3,
        'table_type_map': {
            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'},},
            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
        }
    }
)

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(
    host='localhost', port=7687, params={'user': "neo4j", 'pwd': 'password'})
