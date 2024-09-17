# from ..agents.llama_agent import LLaMAagent
# from ..knowledge_graph_model import KnowledgeGraphModel
# from .utils import QAPipelineConfig

# from .extractor import QALLMGenerator
# from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
# from .knowledge_retriever.TripletsFilter import TripletsFilter
# from .knowledge_retriever.utils import AStarGraphSearchConfig, NaiveTripletsFilterConfig
# from .knowledge_retriever.AStarTripletsRetriever import AStarGraphSearch
# from .updator import KnowledgeComparator
# from .query_parser import QueryLLMParser
# from ..neo4j_functions import Neo4jConnection
# from ..embedding_functions import VectorDBConnectionConfig, EmbeddingsDatabaseConnectionConfig, \
#     EmbeddingsDatabaseConnection, EmbedderModel, EmbedderModelConfig


# class QAPipeline:
#     def __init__(self, kg_model: KnowledgeGraphModel, llm_agent: LLaMAagent, config: QAPipelineConfig) -> None:
#         self.kg_model = kg_model
#         self.llama_agent = llm_agent
#         self.config = config

#         self.query_parser = QueryLLMParser(self.config.query_parser_config, llm_agent)
#         self.knowledge_comparator = KnowledgeComparator(self.config.knowledge_comparator_config)
#         self.knowledge_retriever = KnowledgeRetriever(self.config.knowledge_retriever_config)
#         self.answer_generator = QALLMGenerator(llm_agent, self.config.answer_generator_config)

#     def answer(self, query: str) -> str:
#         # stage 1
#         query_info = self.query_parser.extract_entities(query)
#         # stage 2
#         self.knowledge_comparator.link_kgnodes_to_query(query_info)
#         # stage 3
#         retrieved_triplets = self.knowledge_retriever.retrieve(query_info)
#         # stage 4
#         context = self.answer_generator.formate_context(retrieved_triplets)
#         answer = self.answer_generator.generate(query_info.query, context)

#         return answer


# neo4j_conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")
# nodes_db_config = VectorDBConnectionConfig(path="./nodes", db_name="nodes")
# triplets_db_config = VectorDBConnectionConfig(path="./triplets", db_name="triplets")
# emb_config = EmbedderModelConfig()
# emb_model = EmbedderModel(config=emb_config)
# emb_db_config = EmbeddingsDatabaseConnectionConfig(
#     nodes_db_config=nodes_db_config,
#     triplets_db_config=triplets_db_config,
#     embedder_config=emb_config
# )
# emb_db = EmbeddingsDatabaseConnection(config=emb_db_config)
# kg_model = KnowledgeGraphModel(graph_db=neo4j_conn, embeddings_db=emb_db)

# astar = AStarGraphSearch(kg_model=kg_model)
# astar_config = AStarGraphSearchConfig()
# filter_config = NaiveTripletsFilterConfig()
# filter_model = TripletsFilter(kg_model=kg_model, config=filter_config)
# kn_retr_config = KnowledgeRetrieverConfig(
#     graph_retriever_method=astar,
#     graph_retriever_config=astar_config,
#     triplets_filter_method=filter_model,
#     triplets_filter_config=filter_config
# )

# llm_agent = LLaMAagent()
