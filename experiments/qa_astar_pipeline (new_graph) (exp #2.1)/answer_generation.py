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
from src.knowledge_graph_model import KnowledgeGraphModel, GraphModelConfig, EmbeddingsModelConfig, GraphDriverConfig
from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDBConnectionConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.qa_pipeline import QAPipeline, QAPipelineConfig
from src.qa_pipeline.knowledge_retriever import KnowledgeRetrieverConfig

from src.agents.private import GigaChatAgent
from src.qa_pipeline import QAPipeline
from src.utils import Logger

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
    graph_struct=GraphModelConfig(driver_config=GraphDriverConfig(
        db_vendor='neo4j', db_config=GraphDBConnectionConfig(
            uri=NEO4J_URL, params={'user': NEO4J_USER, 'password': NEO4J_PWD, 'db_name': GRAPH_DB_NAME}))),
    embeddings_struct=EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path=NODES_VECTORDB_PATH, db_name="vectorized_nodes")),
        tripletsdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path=TRIPLETS_VECTORDB_PATH, db_name="vectorized_triplets")),
        embedder_config=EmbedderModelConfig(
        model_name_or_path=EMBEDDING_MODEL_PATH)))

qa_config = QAPipelineConfig(
    knowledge_retriever_config=KnowledgeRetrieverConfig(
        cache_config=KeyValueDriverConfig(
            db_config=KVDBConnectionConfig(
                host='aerospikelservice', port=3000))))

qa_pipeline = QAPipeline(kg_model, agent, config=qa_config)

log = Logger('answer_gen_log')
qa_files = os.listdir(EVAL_DATADIR)
log(qa_files, verbose=False)

for qa_file in qa_files[1:2]:
    log(qa_file, verbose=False)
    s_time = time()
    with open(f"{EVAL_DATADIR}/{qa_file}", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    gen_answers = []
    process = enumerate(data)
    for i, qa_pair in process:
        log(f"[{i} / {len(data)}]", verbose=False)
        answ_gen_s_time = time()
        gen_answer = qa_pipeline.answer(qa_pair['question'])
        gen_answers.append({"generated_answer": gen_answer})
        #process.set_postfix({'target': qa_pair['answer'], 'generated': gen_answer})
        answ_gen_e_time = time()
        log(f"\ttarget: {qa_pair['answer']}", verbose=False)
        log(f"\tgenerated: {gen_answer}", verbose=False)
        log(f"\tanswer_gen_time: {answ_gen_e_time-answ_gen_s_time} sec", verbose=False)


        with open(f"./logs/generated/{qa_file}", 'w', encoding='utf-8') as fd:
            fd.write(json.dumps(gen_answers, indent=1, ensure_ascii=False))

    e_time = time()

    log(f"elapsed_time: {e_time - s_time}", verbose=False)

log("DONE", verbose=False)
