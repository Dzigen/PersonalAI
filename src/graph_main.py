from dataclasses import dataclass, field
from typing import List, Dict
from tqdm import tqdm

from .knowledge_graph_model import GraphModel, GraphModelConfig, EmbeddingsModelConfig, EmbeddingsModel
from .qa_pipeline import QAPipeline, QAPipelineConfig
from .memorize_pipeline import MemPipeline, MemPipelineConfig
from .knowledge_graph_model import KnowledgeGraphModel
from .utils import Logger

RKG_LOG_PATH = "log/rmkg"

@dataclass
class RemoteKnowledgeGraphConfig:
    graph_struct_config: GraphModelConfig = field(default_factory=lambda:GraphModelConfig())
    embedds_struct_config: EmbeddingsModelConfig = field(default_factory=lambda: EmbeddingsModelConfig())
    qa_pipeline_config: QAPipelineConfig = field(default_factory=lambda:QAPipelineConfig())
    mem_pipeline_config: MemPipelineConfig = field(default_factory=lambda:MemPipelineConfig())
    log: Logger = field(default_factory=lambda:Logger(RKG_LOG_PATH))
    verbose: bool = False

class RemoteKnowledgeGraph:
    def __init__(self, config: RemoteKnowledgeGraphConfig):
        self.config = config
        self.log = self.config.log
        
        self.kg_model = KnowledgeGraphModel(
            graph_struct=GraphModel(config.graph_struct_config),
            embeddings_struct=EmbeddingsModel(config.embedds_struct_config))
        self.qa_pipeline = QAPipeline(kg_model=self.kg_model, config=config.qa_pipeline_config)
        self.mem_pipeline = MemPipeline(kg_model=self.kg_model, config=config.mem_pipeline_config)

    def answer_question(self, question: str) -> str:
        self.log("Start answer generation:", verbose=self.config.verbose)
        self.log(f"- question: {question}", verbose=self.config.verbose)
        answer = self.qa_pipeline.answer(question)
        self.log(f"- answer: {answer}", verbose=self.config.verbose)
        return answer

    def update_memory(self, new_info: List[str], properties: List[Dict]):
        self.log("Start memory-updating...", verbose=self.config.verbose)
        for info, props in tqdm(zip(new_info, properties)):
            self.mem_pipeline.remember(info, props)
        self.log("Memory updated successfully!", verbose=self.config.verbose)
            
        
                
        
        
    
        
        

