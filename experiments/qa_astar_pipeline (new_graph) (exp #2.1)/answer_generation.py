import sys
import json
from tqdm import tqdm
import os
from time import time
import gc

# TO CHANGE
BASEDIR = "/workspace"
# TO CHNAGE

sys.path.insert(0, BASEDIR)

EVAL_DATADIR = '../../data/qa_eval'


from src.agents.private import GigaChatAgent
from src.knowledge_graph_model import KnowledgeGraphModel
from src.neo4j_functions import Neo4jConnection
from src.embedding_functions import EmbeddingsDatabaseConnection, EmbeddingsDatabaseConnectionConfig, VectorDBConnectionConfig, EmbedderModelConfig

from src.embedding_functions import VectorDBConnectionConfig, EmbeddingsDatabaseConnectionConfig
from src.agents.private import GigaChatAgent
from src.qa_pipeline import QAPipeline

NEO4J_URL ="bolt://personalai_mmenschikov_neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PWD = "password"
GRAPH_DB_NAME = 'DiaasqGPT4omini'

NODES_VECTORDB_PATH = '../../data/graph_structures/vectorized_nodes/v11/densedb'
TRIPLETS_VECTORDB_PATH = '../../data/graph_structures/vectorized_triplets/v7/densedb'
EMBEDDING_MODEL_PATH = "../../models/intfloat/multilingual-e5-small"
gc.collect()

###########

agent = GigaChatAgent()

kg_model = KnowledgeGraphModel(
    graph_db=Neo4jConnection(uri=NEO4J_URL, user=NEO4J_USER, pwd=NEO4J_PWD, db_name=GRAPH_DB_NAME),
    embeddings_db=EmbeddingsDatabaseConnection(
        config=EmbeddingsDatabaseConnectionConfig(
            nodes_db_config=VectorDBConnectionConfig(
                path=NODES_VECTORDB_PATH,
                db_name="vectorized_nodes"
            ),
            triplets_db_config=VectorDBConnectionConfig(
                path=TRIPLETS_VECTORDB_PATH,
                db_name="vectorized_triplets"
            ),
            embedder_config=EmbedderModelConfig(
                model_name_or_path=EMBEDDING_MODEL_PATH
            )
        )
    )
)


qa_pipeline = QAPipeline(kg_model, agent)

qa_files = os.listdir(EVAL_DATADIR)
for qa_file in qa_files[2:]:
    print(qa_file)
    s_time = time()
    with open(f"{EVAL_DATADIR}/{qa_file}", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    gen_answers = []
    process = tqdm(data)
    for qa_pair in process:
        gen_answer = qa_pipeline.answer(qa_pair['question'])
        gen_answers.append({"generated_answer": gen_answer})
        process.set_postfix({'target': qa_pair['answer'], 'generated': gen_answer})
    e_time = time()

    with open(f"./logs/generated/{qa_file}", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(gen_answers, indent=1, ensure_ascii=False))

    print("elapsed_time: ", e_time - s_time)

print("DONE")