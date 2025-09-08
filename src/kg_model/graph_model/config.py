from ...db_drivers.graph_driver import GraphDriverConfig
from ...db_drivers.graph_driver import GraphDBConnectionConfig
from ...utils import RelationType, NodeType

GRAPH_DB_DEFAULT_DRIVER_CONFIG = GraphDriverConfig(db_vendor='kuzu', db_config=GraphDBConnectionConfig(
    db_info={ 'db': 'default_db','table': 'kuzu_graph' },
    params={'path': '../data/graph_structures/graph_model/kuzu', 'buffer_pool_size': 1024**3,
            'table_type_map': {
                'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'},},
                'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
            }
    }
))
GRAPH_MODEL_LOG_PATH = 'log/kg_model/graph'
