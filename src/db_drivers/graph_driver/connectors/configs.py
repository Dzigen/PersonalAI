from ..utils import GraphDBConnectionConfig
from ....utils.data_structs import NodeType, RelationType


DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig()

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig(
    params={'path': '../../kuzu_volume', 'buffer_pool_size': 1024**3,
            'schema': [
                "CREATE NODE TABLE IF NOT EXISTS object (id SERIAL, name STRING, prop MAP(STRING, STRING), str_id STRING, PRIMARY KEY(id));",
                "CREATE NODE TABLE IF NOT EXISTS hyper (id SERIAL, name STRING, prop MAP(STRING, STRING), str_id STRING, PRIMARY KEY(id));",
                "CREATE NODE TABLE IF NOT EXISTS episodic (id SERIAL, name STRING, prop MAP(STRING, STRING), str_id STRING, PRIMARY KEY(id));",
                "CREATE REL TABLE IF NOT EXISTS simple (FROM object TO object, name STRING, t_id STRING, str_id STRING, prop MAP(STRING, STRING));",
                "CREATE REL TABLE IF NOT EXISTS hyper_rel (FROM object TO hyper, name STRING, t_id STRING, str_id STRING, prop MAP(STRING, STRING));",
                "CREATE REL TABLE GROUP IF NOT EXISTS episodic_rel (FROM object TO episodic, FROM hyper TO episodic, name STRING, t_id STRING, str_id STRING, prop MAP(STRING, STRING));"
            ],
            'table_type_map': {
                'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'},},
                'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
            }
    }
)

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(
    host='localhost', port=7687, params={'user': "neo4j", 'pwd': 'password'})
