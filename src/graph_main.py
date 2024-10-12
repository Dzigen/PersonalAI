import ast
from dataclasses import dataclass, field
from typing import List

from .knowledge_graph_model import GraphModel, GraphModelConfig, EmbeddingsModelConfig, EmbeddingsModel
from .qa_pipeline import QAPipeline, QAPipelineConfig
from .memorize_pipeline import MemPipeline, MemPipelineConfig
from .knowledge_graph_model import KnowledgeGraphModel
from .agents.private import GigaChatAgent
from .utils import Logger

RKG_LOG_PATH = "rmkg_log"

@dataclass
class RemoteKnowledgeGraphConfig:
    graph_sturct_config: GraphModelConfig = field(default_factory=lambda:GraphModelConfig())
    embedds_struct_config: EmbeddingsModelConfig = field(default_factory=lambda: EmbeddingsModelConfig())
    qa_pipeline_config: QAPipelineConfig = field(default_factory=lambda:QAPipelineConfig())
    mem_pipeline_config: MemPipelineConfig = field(default_factory=lambda:MemPipelineConfig())
    log: Logger = field(default_factory=Logger(RKG_LOG_PATH))
    verbose: bool = False

class RemoteKnowledgeGraph:
    def __init__(self, config: RemoteKnowledgeGraphConfig):
        self.config = config
        self.log = self.config.log
        
        self.kg_model = KnowledgeGraphModel(
            graph_struct=GraphModel(config.graph_struct_config),
            embeddings_struct=EmbeddingsModel(config.embedds_struct_config))
        self.llm_agent = GigaChatAgent()
        self.qa_pipeline = QAPipeline(kg_model=self.kg_model, llm_agent=self.llm_agent, config=config.qa_pipeline_config)
        self.mem_pipeline = MemPipeline(agent_conn=self.llm_agent, kg_model=self.kg_model, config=config.mem_pipeline_config)

    def answer_question(self, question: str) -> str:
        self.log("Start answer generation:", verbose=self.config.verbose)
        self.log(f"- question: {question}")
        answer = self.qa_pipeline.answer(question)
        self.log(f"- answer: {answer}")
        return answer

    def update_memory(self, new_info: List[str]):
        self.log("Start memory-updating...", verbose=self.config.verbose)
        for info in new_info:
            self.mem_pipeline.remember(info)
        self.log("Memory updated successfully!", verbose=self.config.verbose)
            
        
                
        
        
    
        
        

