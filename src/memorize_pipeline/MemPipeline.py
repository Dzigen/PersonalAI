from .utils import MemPipelineConfig
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from ..agents import LLaMAagent
from ..qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever
from ..embedding_functions import EmbeddingsDatabaseConnection
from ..neo4j_functions import Neo4jConnection


class MemPipeline:

    def __init__(self, config: MemPipelineConfig, llm_agent: LLaMAagent, bfs: BFSRetriever, neo4j_conn: Neo4jConnection, vectordb_conn: EmbeddingsDatabaseConnection, db_name: str) -> None:
        self.config = config
        self.log = config.log
        self.db_name = db_name

        self.extractor = LLMExtractor(llm_agent, config.extractor_config)
        self.updator = LLMUpdator(config.updator_config, llm_agent, bfs)

        self.neo4j_conn = neo4j_conn
        self.vectordb_conn = vectordb_conn

    def remember(self, text, replacing_window_width = 32, replacing_window_depth = 1, need_simple = True, need_thesises = True, need_episodic = True, 
                 need_update = False, node_prop = {}, rel_prop = {}):
        assert need_simple or need_thesises
        new_triplets = self.extractor.extract(text, need_simple, need_thesises, need_episodic, node_prop, rel_prop)  
        # self.log("PROCESSED NEW TRIPLETS: " + str(new_triplets))

        if need_update:
            triplets_to_remove = self.updator.update(new_triplets, replacing_window_width, replacing_window_depth, need_simple, need_thesises)
            # self.log("PROCESSED OUTDATED TRIPLETS: " + str(triplets_to_remove))
        

        self.neo4j_conn.create_triplets(new_triplets, self.db_name)
        # self.vectordb_conn.add_triplets(new_triplets)
        if need_update:
            self.neo4j_conn.delete_triplets(triplets_to_remove, self.db_name)
        #     self.vectordb_conn.delete_triplets(triplets_to_remove)

    