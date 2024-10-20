from dataclasses import dataclass, field
from typing import Dict, List

from .utils import MEM_LOG_PATH
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from ..qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever
from ..knowledge_graph_model import KnowledgeGraphModel
from ..utils import Logger, Triplet

@dataclass
class MemPipelineConfig:
    """_summary_
    """
    #
    extractor_config: LLMExtractorConfig = field(default_factory=lambda: LLMExtractorConfig())
    #
    updator_config: LLMUpdatorConfig = field(default_factory=lambda: LLMUpdatorConfig())
    #
    log: Logger = field(default_factory=lambda: Logger(MEM_LOG_PATH))
    log_verbose: bool = False

class MemPipeline:

    def __init__(self, kg_model: KnowledgeGraphModel, config: MemPipelineConfig = MemPipelineConfig(), bfs: BFSRetriever = None) -> None:
        """_summary_

        :param kg_model: _description_
        :type kg_model: KnowledgeGraphModel
        :param config: _description_, defaults to MemPipelineConfig()
        :type config: MemPipelineConfig, optional
        :param bfs: _description_, defaults to None
        :type bfs: BFSRetriever, optional
        """
        self.config = config
        self.log = config.log

        self.extractor = LLMExtractor(config.extractor_config)
        # TODO
        #self.updator = LLMUpdator(config.updator_config, bfs)
        
        self.kg_model = kg_model

    def remember(self, text: str, replacing_window_width: int = 32, replacing_window_depth: int = 1, 
                 need_simple: bool = True, need_thesises: bool = True, need_episodic: bool = True, 
                 need_update: bool = False, properties: Dict = dict()) -> List[Triplet]:
        """_summary_

        :param text: _description_
        :type text: str
        :param replacing_window_width: _description_, defaults to 32
        :type replacing_window_width: int, optional
        :param replacing_window_depth: _description_, defaults to 1
        :type replacing_window_depth: int, optional
        :param need_simple: _description_, defaults to True
        :type need_simple: bool, optional
        :param need_thesises: _description_, defaults to True
        :type need_thesises: bool, optional
        :param need_episodic: _description_, defaults to True
        :type need_episodic: bool, optional
        :param need_update: _description_, defaults to False
        :type need_update: bool, optional
        :param properties: _description_, defaults to dict()
        :type properties: Dict, optional
        :return: _description_
        :rtype: List[Triplet]
        """
        assert need_simple or need_thesises
        new_triplets = self.extractor.extract(text, need_simple, need_thesises, need_episodic, properties)  
        self.log("PROCESSED NEW TRIPLETS: " + str(new_triplets), verbose=self.config.log_verbose)

        # TODO
        #if need_update:
        #    triplets_to_remove = self.updator.update(new_triplets, replacing_window_width, replacing_window_depth, need_simple, need_thesises)
        #    self.log("PROCESSED OUTDATED TRIPLETS: " + str(triplets_to_remove))
        
        # В объекты триплетов добавлются идентикаторы, присвоенные им в рамках графовой бд
        self.kg_model.graph_struct.create_triplets(new_triplets)
        self.kg_model.embeddings_struct.add_triplets(new_triplets)
        
        # TODO
        #if need_update:
        #    ids = self.kg_model.graph_struct.delete_triplets(triplets_to_remove)
        #    triplets_ids = [id[1] for id in ids]
        #    nodes_ids = [id[0] for id in ids] + [id[2] for id in ids]
        #    self.kg_model.graph_struct.delete_triplets(triplets_ids, nodes_ids)

        return new_triplets

    