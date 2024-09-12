from ...agents.llama_agent import LLaMAagent
from .utils import LLMExtractorConfig

from typing import List
import ast

class LLMExtractor:

    def __init__(self, llm_agent: LLaMAagent, config: LLMExtractorConfig) -> None:
        self.llm_agent = llm_agent
        self.config = config
        self.triplet_extraction_prompt = config.triplet_extraction_prompt
        self.thesis_extraction_prompt = config.thesis_extraction_prompt
        self.log = config.log
        self.num_hyperedges = 0

    def extract(self, text, need_simple = True, need_thesises = True, need_episodic = True, node_prop = {}, rel_prop = {}):
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
        raw_response = self.llm_agent.generate(self.triplet_extraction_prompt.format(text = text))
        self.log("TEXT: " + text)
        self.log("EXTRACTED TRIPLETS: " + str(raw_response))
        new_triplets = self.parse_triplets(raw_response, node_prop, rel_prop)
        return new_triplets
        
    def extract_thesises(self, text, node_prop = {}, rel_prop = {}):
        raw_response = self.llm_agent.generate(self.thesis_extraction_prompt.format(text = text))
        self.log("TEXT: " + text)
        self.log("EXTRACTED THESISES: " + str(raw_response))
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
    
    def parse_thesises(self, response, node_prop, rel_prop):
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
                        {"name": f'hypernode{self.num_hyperedges}', "type": "hyper", "prop": {"descr": raw_thesis[0], **node_prop}}
                    ]
                )
            self.num_hyperedges += 1
            
        return thesises
    
    @staticmethod
    def parse_triplets(raw_triplets, node_prop, rel_prop):
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
            triplets.append(
                [
                    {"name": subj, "type": "object", "prop": {**node_prop}},
                    {"name": rel, "prop": {"type": "simple", **rel_prop}},
                    {"name": obj, "type": "object", "prop": {**node_prop}}
                ]
            )
        return triplets
    
    def get_episodic_relationships(self, text, entities, node_prop, rel_prop):
        episodic_triplets = []
        for entity in entities:
            triplet = [entity, {"name": "episodic", "prop": {"type": "episodic", **rel_prop}}, 
                       {"name": f'episodicnode{self.num_hyperedges}', "type": "episodic_node", "prop": {"descr": text, **node_prop}}]
            episodic_triplets.append(triplet)
        self.num_hyperedges += 1
            
        return episodic_triplets