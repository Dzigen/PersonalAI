import sys
import pickle

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

from src.graph_main import RemoteKnowledgeGraph, RemoteKnowledgeGraphConfig
from src.knowledge_graph_model import GraphModelConfig, EmbeddingsModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig, DEFAULT_INMEMORYGRAPH_CONFIG
from src.db_drivers.vector_driver import VectorDriverConfig, EmbedderModelConfig, VectorDBConnectionConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig, DEFAULT_INMEMORYKV_CONFIG

from src.qa_pipeline import QAPipelineConfig
from src.qa_pipeline.query_parser import QueryLLMParserConfig
from src.qa_pipeline.knowledge_comparator import KnowledgeComparatorConfig

from src.qa_pipeline.knowledge_retriever import KnowledgeRetrieverConfig
from src.qa_pipeline.knowledge_retriever.AStarTripletsRetriever import AStarGraphSearchConfig
from src.qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSSearchConfig

from src.qa_pipeline.answer_generator import QALLMGeneratorConfig

from src.memorize_pipeline import MemPipelineConfig, LLMExtractorConfig, LLMUpdatorConfig

from src.utils import Logger, ReaderMetrics
from src.utils.data_structs import TripletCreator

PKL_GRAPH_PATH = './all_triplets.pkl'

with open(PKL_GRAPH_PATH, 'rb') as f:
    formated_triplets = pickle.load(f)

print(len(formated_triplets))

inmemory_kg_config = RemoteKnowledgeGraphConfig(
    
    graph_struct_config=GraphModelConfig(driver_config=GraphDriverConfig(
        db_vendor='inmemory_graph', db_config=DEFAULT_INMEMORYGRAPH_CONFIG)), # TO CHANGE
    
    embedds_struct_config=EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            path='../../data/graph_structures/vectorized_nodes/testing6', db_name='vectorized_nodes', is_exist=False, need_to_clear=False)), # TO CHANGE
        tripletsdb_driver_config=VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            path='../../data/graph_structures/vectorized_triplets/testing6', db_name='vectorized_triplets', is_exist=False, need_to_clear=False)), # TO CHANGE
        embedder_config=EmbedderModelConfig(model_name_or_path='intfloat/multilingual-e5-small')),
    
    qa_pipeline_config=QAPipelineConfig(
        query_parser_config=QueryLLMParserConfig(),
        knowledge_comparator_config=KnowledgeComparatorConfig(),
        knowledge_retriever_config=KnowledgeRetrieverConfig(
            retriever_method='bfs', # TO CHANGE
            retriever_config=BFSSearchConfig(), # TO CHANGE
            cache_config=KeyValueDriverConfig(db_vendor='inmemory_kv', db_config=DEFAULT_INMEMORYKV_CONFIG)), # TO CHANGE
        answer_generator_config=QALLMGeneratorConfig()),
    
    mem_pipeline_config=MemPipelineConfig(
        extractor_config=LLMExtractorConfig(),
        updator_config=LLMUpdatorConfig()),
    
    log=Logger('log/main'))

rkg_main = RemoteKnowledgeGraph(config=inmemory_kg_config)

rkg_main.kg_model.graph_struct.create_triplets(formated_triplets)
rkg_main.kg_model.embeddings_struct.add_triplets(formated_triplets)

examples_questions = [
    "Какой ущерб государству от потери одного гражданина?", # 8.2 mln
    "Сколько экстренных вызовов было принято в 2022 году?", # >10 mln
    "Сколько экстренных вызовов было передано в экстренные службы в 2022 году?", # 78 675
    "На чем основан успех Яндекса?", # на сильной команде  и технологиях собственной разработки
    "Перечисли 8 умных устройств умного дома, продаваемых сбером в 2023 году" # Управляющий хаб  • Сценарная кнопка  • Розетка  • Детский светильник  • Датчики открытия  • Датчики движения  • Датчики протечки  • Датчики температуры и влажности
]

for question in examples_questions:
    print(rkg_main.answer_question(question))
    print("=" * 35)