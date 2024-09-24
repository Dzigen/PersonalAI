from .utils import log_path
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from ..llm_agent import AgentConnector
from ..qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever
from ..utils.data_structs import Triplet, Node, Relation, TripletCreator, NodeCreator, NODES_TYPES_MAP, RELATIONS_TYPES_MAP
from ..knowledge_graph_model import KnowledgeGraphModel
from ..utils import Logger

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class MemPipelineConfig:
    extractor_config: LLMExtractorConfig = field(default_factory=lambda: LLMExtractorConfig())
    updator_config: LLMUpdatorConfig = field(default_factory=lambda: LLMUpdatorConfig())
    log: Logger = field(default_factory=lambda: Logger(log_path))

class MemPipeline:

    def __init__(self, agent_conn: AgentConnector, bfs: BFSRetriever, kg_model: KnowledgeGraphModel, config: MemPipelineConfig = MemPipelineConfig()) -> None:
        self.config = config
        self.log = config.log

        self.extractor = LLMExtractor(agent_conn, config.extractor_config)
        self.updator = LLMUpdator(config.updator_config, agent_conn, bfs)
        
        self.kg_model = kg_model

    def remember(self, text: str, replacing_window_width: int = 32, replacing_window_depth: int = 1, 
                 need_simple: bool = True, need_thesises: bool = True, need_episodic: bool = True, 
                 need_update: bool = False, node_prop: Dict = {}, rel_prop: Dict = {}) -> None:
        assert need_simple or need_thesises
        new_triplets = self.extractor.extract(text, need_simple, need_thesises, need_episodic, node_prop, rel_prop)  
        # self.log("PROCESSED NEW TRIPLETS: " + str(new_triplets))

        if need_update:
            triplets_to_remove = self.updator.update(new_triplets, replacing_window_width, replacing_window_depth, need_simple, need_thesises)
            # self.log("PROCESSED OUTDATED TRIPLETS: " + str(triplets_to_remove))
        
        # В объекты триплетов добавлются идентикаторы, присвоенные им в рамках графовой бд
        self.kg_model.graph_db.create_triplets(new_triplets)
        self.kg_model.embeddings_db.add_triplets(new_triplets)
        if need_update:
            ids = self.kg_model.graph_db.delete_triplets(triplets_to_remove)
            triplets_ids = [id[1] for id in ids]
            nodes_ids = [id[0] for id in ids] + [id[2] for id in ids]
            self.kg_model.embeddings_db.delete_triplets(triplets_ids, nodes_ids)


    