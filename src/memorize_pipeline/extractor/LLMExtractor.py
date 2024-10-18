
from dataclasses import dataclass, field
from typing import List, Dict
import ast

from .utils import MEM_EXTRACT_LOG_PATH, MEM_EXTRACT_TRIPLET_SYSTEM_PROMPT, MEM_EXTRACT_TRIPLET_USER_PROMPT, MEM_EXTRACT_THESIS_SYSTEM_PROMPT, MEM_EXTRACT_THESIS_USER_PROMPT
from ...utils import Logger
from ...utils.data_structs import TripletCreator, NodeCreator, Node, Relation, RelationType, NodeType, Triplet
from ...agents import AgentDriver, AgentDriverConfig

@dataclass
class LLMExtractorConfig:
    lang: str = "ru"
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig)
    triplet_extract_system_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_SYSTEM_PROMPT)
    triplet_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_USER_PROMPT)
    thesis_extract_system_prompt:  dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_SYSTEM_PROMPT)
    thesis_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_USER_PROMPT)
    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACT_LOG_PATH))
    verbose: bool = False

class LLMExtractor:

    def __init__(self, config: LLMExtractorConfig = LLMExtractorConfig()) -> None:
        self.config = config
        self.agent = AgentDriver.connect(config.agent_config)
        self.log = config.log
        self.num_hyperedges = 0

    def extract(self, text: str, need_simple: bool = True, need_thesises: bool = True, 
                need_episodic: bool = True, properties: Dict = {}) -> List[Triplet]:
        assert need_simple or need_thesises
        self.log("START EXTRACTION...", verbose=self.config.verbose)
        new_triplets = []
        if need_simple:
            new_triplets += self.extract_triplets(text, rel_prop=properties)
            
        if need_thesises:
            new_triplets += self.extract_thesises(text, node_prop=properties)
            
        if need_episodic:
            new_triplets += self.get_episodic_relationships(
                text, self.get_entities_from_triplets(new_triplets), node_prop=properties)
            
        return new_triplets

    def extract_triplets(self, text: str, node_prop = {}, rel_prop = {}) -> List[Triplet]:
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            self.config.triplet_extract_system_prompt[self.config.lang],
            self.config.triplet_extract_user_prompt[self.config.lang].format(text=text))
        self.log("EXTRACTED TRIPLETS: " + str(raw_response), verbose=self.config.verbose)
        new_triplets = self.parse_triplets(raw_response, node_prop, rel_prop)
        return new_triplets
        
    def extract_thesises(self, text: str, node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            self.config.thesis_extract_system_prompt[self.config.lang],
            self.config.thesis_extract_user_prompt.format(text=text))
        self.log("EXTRACTED THESISES: " + str(raw_response), verbose=self.config.verbose)
        new_triplets = self.parse_thesises(raw_response, node_prop, rel_prop)
        return new_triplets
    
    @staticmethod
    def get_entities_from_triplets(triplets: List[Triplet]) -> List[Node]:
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())
    
    @staticmethod
    def parse_thesises(response: str, node_prop: Dict, rel_prop: Dict) -> List[Triplet]:
        #raw_triplets = ' '.join(list(filter(lambda v: len(v) and (';' in v) and ('.' in v), response.split("\n")[1:-1]))).lower()
        if ":" in response:
            response = response.split(":")[-1]  
        raw_thesises = response.split(".")
        thesises = []
        for raw_thesis in raw_thesises:
            if ";" not in raw_thesis:
                continue
            try:
                raw_thesis, raw_entities = raw_thesis.split(";")
                thesis = raw_thesis.strip('.-* ')
                entities = ast.literal_eval(raw_entities.strip(''' \n'".,/'''))
            except:
                continue
            
            thesis_node = NodeCreator.create(name=str(thesis), type=NodeType.hyper, prop={**node_prop})
            thesis_rel = Relation(name=RelationType.hyper.value, type=RelationType.hyper, prop={**rel_prop})
            for entity in entities:
                thesises.append(TripletCreator.create(
                    NodeCreator.create(name=str(entity), type=NodeType.object, prop={**node_prop}),
                    thesis_rel, thesis_node))
            
        return thesises
    
    @staticmethod
    def parse_triplets(raw_triplets: str, node_prop: Dict, rel_prop: Dict) -> List[Triplet]:
        #raw_triplets = ' '.join(list(filter(lambda v: len(v), raw_triplets.split("\n")[1:-1]))).lower()
        if ":" in raw_triplets:
            raw_triplets = raw_triplets.split(":")[-1]
        raw_triplets = raw_triplets.lower()
        raw_triplets = raw_triplets.split(";")
        triplets = []
        for triplet in raw_triplets:
            if len(triplet.split(",")) != 3:
                continue
            subj, rel, obj = triplet.split(",")
            subj, rel, obj = subj.split(":")[-1].split(".")[-1].strip(''' \n'".,/'''), rel.strip(''' \n'".,/'''), obj.strip(''' \n'".,/''')
            if len(subj) == 0 or len(rel) == 0 or len(obj) == 0:
                continue

            triplets.append(TripletCreator.create(
                NodeCreator.create(name=str(subj), type=NodeType.object, prop={**node_prop}),
                Relation(name=str(rel), type=RelationType.simple, prop={**rel_prop}),
                NodeCreator.create(name=str(obj), type=NodeType.object, prop={**node_prop})))

        return triplets
    
    @staticmethod
    def get_episodic_relationships(text: str, entities: List[Node], node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        episodic_node = NodeCreator.create(name=text, type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(name=RelationType.episodic.value, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets