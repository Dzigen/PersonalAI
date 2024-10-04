from ...llm_agent import AgentConnector
from .utils import TRIPLETS_EXTRACTION_PROMPT_ENG, THESISES_EXTRACTION_PROMPT_ENG, \
                    TRIPLETS_EXTRACTION_PROMPT, THESISES_EXTRACTION_PROMPT, \
                    TRIPLETS_EXTRACTION_PROMPT_ENG_SYSTEM, THESISES_EXTRACTION_PROMPT_ENG_SYSTEM, \
                    TRIPLETS_EXTRACTION_PROMPT_SYSTEM, THESISES_EXTRACTION_PROMPT_SYSTEM, \
                    TRIPLETS_EXTRACTION_PROMPT_ENG_USER, THESISES_EXTRACTION_PROMPT_ENG_USER, \
                    TRIPLETS_EXTRACTION_PROMPT_USER, THESISES_EXTRACTION_PROMPT_USER, \
                    Logger, log_path
from ...utils.data_structs import TripletCreator, NodeCreator, NODES_TYPES_MAP, RELATIONS_TYPES_MAP, Node, Relation, RelationType, NodeType, Triplet

from dataclasses import dataclass, field
from typing import List, Dict
import ast

@dataclass
class LLMExtractorConfig:
    triplet_extraction_prompt: str = TRIPLETS_EXTRACTION_PROMPT_ENG
    thesis_extraction_prompt: str = THESISES_EXTRACTION_PROMPT_ENG
    
    triplet_extraction_prompt_system: str = TRIPLETS_EXTRACTION_PROMPT_ENG_SYSTEM
    thesis_extraction_prompt_system: str = THESISES_EXTRACTION_PROMPT_ENG_SYSTEM
    
    triplet_extraction_prompt_user: str = TRIPLETS_EXTRACTION_PROMPT_ENG_USER
    thesis_extraction_prompt_user: str = THESISES_EXTRACTION_PROMPT_ENG_USER
    log: Logger = field(default_factory=lambda: Logger(log_path))
    verbose: bool = False

class LLMExtractor:

    def __init__(self, agent_conn: AgentConnector, config: LLMExtractorConfig = LLMExtractorConfig()) -> None:
        self.agent_conn = agent_conn
        self.config = config
        self.triplet_extraction_prompt = config.triplet_extraction_prompt
        self.thesis_extraction_prompt = config.thesis_extraction_prompt
        
        self.triplet_extraction_prompt_system = config.triplet_extraction_prompt_system
        self.thesis_extraction_prompt_system = config.thesis_extraction_prompt_system
        
        self.triplet_extraction_prompt_user = config.triplet_extraction_prompt_user
        self.thesis_extraction_prompt_user = config.thesis_extraction_prompt_user
        self.log = config.log
        self.num_hyperedges = 0

    def extract(self, text: str, need_simple: bool = True, need_thesises: bool = True, 
                need_episodic: bool = True, node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        assert need_simple or need_thesises
        new_triplets = []
        if need_simple:
            new_triplets += self.extract_triplets(text, node_prop, rel_prop)
            
        if need_thesises:
            new_triplets += self.extract_thesises(text, node_prop, rel_prop)
            
        if need_episodic:
            new_triplets += self.get_episodic_relationships(
                text, self.get_entities_from_triplets(new_triplets), node_prop, rel_prop)
            
        return new_triplets

    def extract_triplets(self, text: str, node_prop = {}, rel_prop = {}) -> List[Triplet]:
        raw_response = self.agent_conn.generate(self.triplet_extraction_prompt_user.format(text = text), 
                                                system_prompt = self.triplet_extraction_prompt_system)
        self.log("TEXT: " + text, verbose=self.config.verbose)
        self.log("EXTRACTED TRIPLETS: " + str(raw_response), verbose=self.config.verbose)
        new_triplets = self.parse_triplets(raw_response, node_prop, rel_prop)
        return new_triplets
        
    def extract_thesises(self, text: str, node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        raw_response = self.agent_conn.generate(self.thesis_extraction_prompt.format(text=text))
        self.log("TEXT: " + text, verbose=self.config.verbose)
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
            
            thesis_node = NodeCreator.create(name=thesis, type=NodeType.hyper, prop={**node_prop})
            thesis_rel = Relation(name=RelationType.hyper, type=RelationType.hyper, prop={**rel_prop})
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
                NodeCreator.create(name=subj, type=NodeType.object, prop={**node_prop}),
                Relation(name=rel, type=RelationType.simple, prop={**rel_prop}),
                NodeCreator.create(name=obj, type=NodeType.object, prop={**node_prop})))

        return triplets
    
    @staticmethod
    def get_episodic_relationships(text: str, entities: List[Node], node_prop: Dict, rel_prop: Dict) -> List[Triplet]:
        episodic_node = NodeCreator.create(name=text, type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(name=RelationType.episodic, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets