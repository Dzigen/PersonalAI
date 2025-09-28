from src.utils import Logger
from src.qa_pipeline.answer_generator import QALLMGeneratorConfig
from src.qa_pipeline.knowledge_retriever import KnowledgeRetrieverConfig, AStarGraphSearchConfig
from src.qa_pipeline import QAPipeline, QAPipelineConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.db_drivers.graph_driver import GraphDBConnectionConfig
from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, EmbedderModelConfig
from src.knowledge_graph_model import KnowledgeGraphModel, GraphModelConfig, EmbeddingsModelConfig, GraphDriverConfig, GraphModel, EmbeddingsModel
from src.knowledge_graph_model import KnowledgeGraphModel, DEFAULT_NEO4J_CONFIG
from src.agents.private import GigaChatAgent
import sys
import json
from tqdm import tqdm
import os
from time import time
import gc

# TO CHANGE
# BASEDIR = "/workspace"
BASEDIR = "../../"
# TO CHNAGE

sys.path.insert(0, BASEDIR)

EVAL_DATADIR = '../../data/qa_eval'


AEROSPIKE_URL = "127.0.0.1"  # 'aerospikelservice_gigachat'
AEROSPIKE_PORT = 3000

NODES_VECTORDB_PATH = '../../data/graph_structures/vectorized_nodes/v8/densedb'
TRIPLETS_VECTORDB_PATH = '../../data/graph_structures/vectorized_triplets/v4/densedb'
EMBEDDING_MODEL_PATH = "../../models/intfloat/multilingual-e5-small"
gc.collect()

###########

agent = GigaChatAgent()

GRAPH_CONFIG = GraphModelConfig(driver_config=GraphDriverConfig(
    db_vendor='neo4j', db_config=DEFAULT_NEO4J_CONFIG))

EMBEDDINGS_CONFIG = EmbeddingsModelConfig(
    nodesdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
        path=NODES_VECTORDB_PATH, db_name="vectorized_nodes", need_to_clear=False)),
    tripletsdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
        path=TRIPLETS_VECTORDB_PATH, db_name="vectorized_triplets", need_to_clear=False)),
    embedder_config=EmbedderModelConfig(model_name_or_path=EMBEDDING_MODEL_PATH))

QA_CONFIG = QAPipelineConfig(
    knowledge_retriever_config=KnowledgeRetrieverConfig(
        retriever_method='astar',
        retriever_config=AStarGraphSearchConfig(),  # TO CHANGE
        cache_config=KeyValueDriverConfig(db_vendor='aerospike', db_config=KVDBConnectionConfig(
            host=AEROSPIKE_URL, port=AEROSPIKE_PORT))),  # TO CHANGE
    answer_generator_config=QALLMGeneratorConfig(lang='eng'))

###########

kg_model = KnowledgeGraphModel(graph_struct=GraphModel(
    GRAPH_CONFIG), embeddings_struct=EmbeddingsModel(EMBEDDINGS_CONFIG))
qa_pipeline = QAPipeline(kg_model, agent, config=QA_CONFIG)

###########

log = Logger('log/answer_gen')
qa_files = os.listdir(EVAL_DATADIR)
log(qa_files, verbose=False)
for qa_file in qa_files[-1:]:
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
        # process.set_postfix({'target': qa_pair['answer'], 'generated': gen_answer})
        answ_gen_e_time = time()
        log(f"\ttarget: {qa_pair['answer']}", verbose=False)
        log(f"\tgenerated: {gen_answer}", verbose=False)
        log(f"\tanswer_gen_time: {answ_gen_e_time-answ_gen_s_time} sec", verbose=False)

        with open(f"./logs/generated/{qa_file}", 'w', encoding='utf-8') as fd:
            fd.write(json.dumps(gen_answers, indent=1, ensure_ascii=False))

    e_time = time()
    log(f"elapsed_time: {e_time - s_time}", verbose=False)

log("DONE", verbose=False)
