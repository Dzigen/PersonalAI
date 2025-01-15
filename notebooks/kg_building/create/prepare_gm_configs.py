import sys
import joblib

BASEDIR = '/home/m.menschikov/workspace/Personal-AI' # TO CHANGE
sys.path.insert(0, BASEDIR)

from src.kg_model import EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDBConnectionConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig

GRAPHDB_CONFIG_DUMP = "graphdb_config"

graphdb_config = GraphDBConnectionConfig(
    uri=f"bolt://personalai_mmenschikov_neo4j:7687", params={'user': "neo4j", 'pwd': 'password'},
    need_to_clear=True)

NODESDB_CONFIG_DUMP = "nodesdb_config"

nodesdb_config=VectorDBConnectionConfig(
    db_info={'db': 'personalaidb', 'table': "vectorized_nodes"},
    need_to_clear=False)

TRIPLETSDB_CONFIG_DUMP = "tripletsdb_config"

tripletsdb_config=VectorDBConnectionConfig(
    db_info={'db': 'personalaidb', 'table': "vectorized_triplets"},
    need_to_clear=False)

EMBEDDER_CONFIG_DUMP = 'embedder_config'

embedder_config=EmbedderModelConfig(
    model_name_or_path='/home/m.menschikov/workspace/Personal-AI/models/intfloat/multilingual-e5-small')

print("graphdb: ", graphdb_config)
print("nodesdb: ", nodesdb_config)
print("tripletsdb: ", tripletsdb_config)
print("embedder: ", embedder_config)

joblib.dump(graphdb_config, GRAPHDB_CONFIG_DUMP)
joblib.dump(nodesdb_config, NODESDB_CONFIG_DUMP)
joblib.dump(tripletsdb_config, TRIPLETSDB_CONFIG_DUMP)
joblib.dump(embedder_config, EMBEDDER_CONFIG_DUMP)
