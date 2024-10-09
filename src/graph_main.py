import ast
from dataclasses import dataclass, field
from typing import List

from .neo4j_functions import Neo4jConnection, Neo4jConnectionConfig
from .agents.private import GigaChatAgent
from .utils import Logger
from .qa_pipeline import QAPipeline, QAPipelineConfig
from .memorize_pipeline import MemPipeline, MemPipelineConfig
from .knowledge_graph_model import KnowledgeGraphModel
from .embedding_functions import EmbeddingsDatabaseConnection, EmbeddingsDatabaseConnectionConfig

RKG_LOG_PATH = "rmkg_log"

@dataclass
class RemoteKnowledgeGraphConfig:
    graph_db_config: Neo4jConnectionConfig
    embedder_db_config: EmbeddingsDatabaseConnectionConfig
    qa_pipeline_config: QAPipelineConfig = field(default_factory=lambda:QAPipelineConfig())
    mem_pipeline_config: MemPipelineConfig = field(default_factory=lambda:MemPipelineConfig())
    log: Logger = field(default_factory=Logger(RKG_LOG_PATH))
    log_verbose: bool = False

class RemoteKnowledgeGraph:
    def __init__(self, config: RemoteKnowledgeGraphConfig):
        self.config = config
        self.log = self.config.log
        
        self.kg_model = KnowledgeGraphModel(
            graph_db=Neo4jConnection(config.graph_db_config),
            embeddings_db=EmbeddingsDatabaseConnection(config.embedder_db_config))
        self.llm_agent = GigaChatAgent()
        self.qa_pipeline = QAPipeline(kg_model=self.kg_model, llm_agent=self.llm_agent, config=config.qa_pipeline_config)
        self.mem_pipeline = MemPipeline(agent_conn=self.llm_agent, kg_model=self.kg_model, config=config.mem_pipeline_config)

    def answer_question(self, question: str) -> str:
        return self.qa_pipeline.answer(question)

    def update_memory(self, new_info: List[str]):
        for info in new_info:
            self.mem_pipeline.remember(info)
        
                
        
        
    
        
        

