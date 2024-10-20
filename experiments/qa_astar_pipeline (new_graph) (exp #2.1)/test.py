import sys
import json
from tqdm import tqdm
from typing import Dict
import numpy as np
import torch
import os
from time import time
import gc

# TO CHANGE
BASEDIR = "/workspace"
# TO CHNAGE

sys.path.insert(0, BASEDIR)

EVAL_DATADIR = '../../data/qa_eval'

from src.qa_pipeline import QAPipeline, QAPipelineConfig
from src.qa_pipeline.query_parser import QueryLLMParser
from src.qa_pipeline.knowledge_comparator import KnowledgeComparator
from src.qa_pipeline.knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig, AStarGraphSearchConfig
from src.qa_pipeline.knowledge_retriever.AStarTripletsRetriever import AStarMetricsConfig
from src.qa_pipeline.answer_generator import QALLMGenerator

from src.agents.private import GigaChatAgent
from src.knowledge_graph_model import KnowledgeGraphModel
from src.db_models.graph_db.neo4j_functions import Neo4jConnection
from src.db_models.embeddings_db.embedding_functions import EmbeddingsDatabaseConnection, EmbeddingsDatabaseConnectionConfig, VectorDBConnectionConfig, EmbedderModelConfig

from src.utils import ReaderMetrics
from src.db_models.embeddings_db.embedding_functions import ChromaConnection, VectorDBConnectionConfig, EmbeddingsDatabaseConnectionConfig
from src.agents.private import GigaChatAgent
from src.utils.data_structs import NodeType

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

QUERIES = [
    "Which device is better in battery life: iPhone11 Pro Max or Xiaomi 11?", # быстро X
    "The majority of speakers have positive, neutral or negative sentiment about connection of Apple?", # ~1 min X
    "The majority of speakers have positive, neutral or negative sentiment about signal of Apple?", # ~28sec X
    "Kayla has positive, negative or neutral opinion about video of 10PRO on 25.11.2020?", # ~ 2 min X
    "What Jessica's opinion (positive, negative or neutral) about signal of Apple was dominant during using Apple?", # ~ 25sec X
    "What opinion (positive, negative or neutral) about scheduling of IQOO9 was last during Zachary's experience of IQOO9?", # ~ 38sec
    "Do Jane and Jonathan have any common devices (which Jane and Jonathan both use)? If so, list common devices. Otherwise, answer 'No'.", # ~8sec X
    "Do Maria and Tyler prefer the same device manufacturer? If so, list common manufacturers. Otherwise, answer 'No'.", # ~42sec X
    "Whose opinions from Freda and Bruce about devices are most similar to Kayla's?", # ~26sec X
    "Whose opinions from Linda and Arianna about manufacturers are most similar to Hugh's?", # 1.20min X
    "Which people have positive opinion about display of Mi 10pro on 22.12.2018?", # ~ 2 min X
    "Which people have negative opinion about video of 10PRO on 25.11.2020?" # ~ 2 min X
    ]

qa_pipeline = QAPipeline(kg_model, agent)

###########

for query in tqdm(QUERIES):
    s_time = time()
    answer = qa_pipeline.answer(query)
    e_time = time()
    print(answer, e_time - s_time)
