from src.memorize_pipeline.MemPipeline import MemPipeline
from src.memorize_pipeline.utils import MemPipelineConfig
from src.agents.llama_agent import LLaMAagentLocal
from src.qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever
from src.knowledge_graph_model import KnowledgeGraphModel
from src.neo4j_functions import Neo4jConnection
from src.embedding_functions import EmbeddingsDatabaseConnection
from src.embedding_functions import EmbeddingsDatabaseConnectionConfig, VectorDBConnectionConfig, EmbedderModelConfig

import json

mem_pipe_config = MemPipelineConfig()
llm_agent = LLaMAagentLocal("You are a helpful assistant")

uri, user, pwd = "bolt://31.207.47.254:7687", 'neo4j', 'password'
neo4j_conn = Neo4jConnection(uri, user, pwd)
db_name = "testMem"
neo4j_conn.execute_query(f"CREATE DATABASE {db_name} IF NOT EXISTS")

triplets_db_config = VectorDBConnectionConfig("test_path_triplets", "test_db_triplets")
nodes_db_config = VectorDBConnectionConfig("test_path_nodes", "test_db_nodes")
emb_config = EmbedderModelConfig(device = "cpu")

vectordb_config = EmbeddingsDatabaseConnectionConfig(nodes_db_config, triplets_db_config, emb_config)
vectordb_conn = EmbeddingsDatabaseConnection(vectordb_config)

kg_model = KnowledgeGraphModel(neo4j_conn, vectordb_conn)

bfs = BFSRetriever(kg_model)

mem_pipe = MemPipeline(mem_pipe_config, llm_agent, bfs, neo4j_conn, vectordb_conn, db_name)

with open("Augment_DiaASQ.json") as f:
    data = json.load(f)

facts = [dialog["text_dialog"] for dialog in data["data"]][:15]
for fact in facts:
    mem_pipe.remember(fact, node_prop={}, rel_prop = {"time": 1})
