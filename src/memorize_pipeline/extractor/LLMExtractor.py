from ...llm_agent import AgentConnector
from .utils import TRIPLETS_EXTRACTION_PROMPT, THESISES_EXTRACTION_PROMPT, Logger, log_path

from dataclasses import dataclass, field
from typing import List, Dict
import ast

@dataclass
class LLMExtractorConfig:
    triplet_extraction_prompt: str = TRIPLETS_EXTRACTION_PROMPT
    thesis_extraction_prompt: str = THESISES_EXTRACTION_PROMPT
    log: Logger = field(default_factory=lambda: Logger(log_path))

class LLMExtractor:

    def __init__(self, agent_conn: AgentConnector, config: LLMExtractorConfig =  LLMExtractorConfig()) -> None:
        self.agent_conn = agent_conn
        self.config = config
        self.triplet_extraction_prompt = config.triplet_extraction_prompt
        self.thesis_extraction_prompt = config.thesis_extraction_prompt
        self.log = config.log

    def extract(self, text: str, need_simple = True, need_thesises = True, need_episodic = True, node_prop = {}, rel_prop = {}):
        assert need_simple or need_thesises
        new_triplets = []
        if need_simple:
            new_simple_triplets = self.extract_triplets(text, node_prop, rel_prop)
            new_triplets += new_simple_triplets

        if need_thesises:
            new_thesises_triplets = self.extract_thesises(text, node_prop, rel_prop)
            new_triplets += new_thesises_triplets
        
        if need_episodic:
            new_triplets += self.get_episodic_relationships(text, self.get_entities_from_triplets(new_triplets), node_prop, rel_prop)
            
        return new_triplets

    def extract_triplets(self, text, node_prop = {}, rel_prop = {}):
        raw_response = self.agent_conn.generate(self.triplet_extraction_prompt.format(text = text), 
                                                gen_strategy={'max_new_tokens': 2048})
        self.log("TEXT: " + text, verbose=False)
        self.log("EXTRACTED TRIPLETS: " + str(raw_response), verbose=False)
        new_triplets = self.parse_triplets(raw_response, node_prop, rel_prop)
        return new_triplets
        
    def extract_thesises(self, text, node_prop = {}, rel_prop = {}):
        raw_response = self.agent_conn.generate(self.thesis_extraction_prompt.format(text = text), 
                                                gen_strategy={'max_new_tokens': 2048})
        self.log("TEXT: " + text, verbose=False)
        self.log("EXTRACTED THESISES: " + str(raw_response), verbose=False)
        new_triplets = self.parse_thesises(raw_response, node_prop, rel_prop)
        return new_triplets
    
    @staticmethod
    def get_entities_from_triplets(triplets):
        entities = []
        for triplet in triplets:
            if triplet[0] not in entities:
                entities.append(triplet[0])
            if triplet[2] not in entities:
                entities.append(triplet[2])
        return entities
    
    @staticmethod
    def parse_thesises(response, node_prop, rel_prop):
        if ":" in response:
            response = response.split(":")[-1]
        raw_thesises = response.split(".")
        thesises = []
        for raw_thesis in raw_thesises:
            if ";" not in raw_thesis:
                continue
            raw_thesis = raw_thesis.split(";")
            try:
                entities = ast.literal_eval(raw_thesis[1].strip(''' \n'".,/'''))
            except:
                continue
            
            for entity in entities:
                thesises.append(
                    [
                        {"name": entity, "type": "object", "prop": {**node_prop}},
                        {"name": "hyper", "prop": {"type": "simple", **rel_prop}},
                        {"name": raw_thesis[0], "type": "hyper", "prop": {**node_prop}}
                    ]
                )
            
        return thesises
    
    @staticmethod
    def parse_triplets(raw_triplets: str, node_prop: Dict, rel_prop: Dict):
        raw_triplets = ' '.join(list(filter(lambda v: len(v), raw_triplets.split("\n")[1:-1]))).lower()
        raw_triplets = raw_triplets.split(";")
        triplets = []
        for triplet in raw_triplets:
            if len(triplet.split(",")) != 3:
                continue
            subj, rel, obj = triplet.split(",")
            subj, rel, obj = subj.split(":")[-1].split(".")[-1].strip(''' \n'".,/'''), rel.strip(''' \n'".,/'''), obj.strip(''' \n'".,/''')
            if len(subj) == 0 or len(rel) == 0 or len(obj) == 0:
                continue
            triplets.append(
                [
                    {"name": subj, "type": "object", "prop": {**node_prop}},
                    {"name": rel, "prop": {"type": "simple", **rel_prop}},
                    {"name": obj, "type": "object", "prop": {**node_prop}}
                ]
            )
        return triplets
    
    @staticmethod
    def get_episodic_relationships(text, entities, node_prop, rel_prop):
        episodic_triplets = []
        for entity in entities:
            triplet = [entity, {"name": "episodic", "prop": {"type": "episodic", **rel_prop}}, 
                       {"name": text, "type": "episodic_node", "prop": {**node_prop}}]
            episodic_triplets.append(triplet)
            
        return episodic_triplets