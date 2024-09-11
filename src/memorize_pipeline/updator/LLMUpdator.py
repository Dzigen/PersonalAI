from .utils import LLMUpdatorConfig
from ...knowledge_graph_model import KnowledgeGraphModel
from ...embedding_functions import VectorDBInstance
from ...agents import LLaMAagent
from ...qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever

class LLMUpdator:

    def __init__(self, config: LLMUpdatorConfig, llm_agent: LLaMAagent, bfs: BFSRetriever) -> None:
        self.config = config
        self.llm_agent = llm_agent
        self.bfs = bfs

        self.replace_simple_prompt = config.replace_simple_prompt
        self.replace_thesis_prompt = config.replace_thesis_prompt
        self.log = config.log

    def update(self, new_triplets, replacing_window_width, replacing_window_depth, need_simple = True, need_thesises = True):
        assert need_simple or need_thesises
        entities = self.get_entities_from_triplets(new_triplets)  
        triplets_to_remove = []  
        
        if need_simple:    
            ex_triplets = self.bfs.bfs_(entities, replacing_window_depth, edge_types = ["simple"], max_triplets = replacing_window_width)
            if ex_triplets:
                replacements = self.llm_agent.generate(self.replace_simple_prompt.format(ex_triplets = self.stringify_all(ex_triplets), 
                                                                        new_triplets = self.stringify_all(new_triplets)))
                self.log("FOUND SIMPLE REPLACEMENTS: " + str(replacements))
                triplets_to_remove += self.parse_replacements_simple(replacements)
            else:
                self.log("FOUND NO EXISTED SIMPLE TRIPLETS TO REMOVE")
            
        if need_thesises:    
            ex_triplets = self.bfs.bfs_(entities, replacing_window_depth, edge_types = ["hyper"], max_triplets = replacing_window_width)
            if ex_triplets:
                replacements = self.llm_agent.generate(self.replace_thesis_prompt.format(ex_triplets = self.stringify_all(ex_triplets), 
                                                                        new_triplets = self.stringify_all(new_triplets)))
                self.log("FOUND THESIS REPLACEMENTS: " + str(replacements))
                triplets_to_remove += self.parse_replacements_thesis(replacements)
            else:
                self.log("FOUND NO EXISTED THESIS TRIPLETS TO REMOVE")
            
        return triplets_to_remove
    
    @staticmethod
    def parse_replacements_simple(raw_replacements):
        raw_replacements = raw_replacements.lower()
        raw_replacements = raw_replacements.split("[[")[-1] if "[[" in raw_replacements else raw_replacements.split("[\n[")[-1]
        pairs = raw_replacements.replace("[", "").strip("]").split("],")
        triplets_to_remove = []
        for pair in pairs:
            splitted_pair = pair.split("->")
            if len(splitted_pair) != 2:
                continue
            first_triplet = splitted_pair[0].split(",")
            if len(first_triplet) != 3:
                continue
            subj, rel, obj = first_triplet[0].strip(''' \n'".,/'''), first_triplet[1].strip(''' \n'".,/'''), first_triplet[2].strip(''' \n'".,/''')
            triplets_to_remove.append(
                [
                    {"name": subj, "type": "remove", "prop": {}},
                    {"name": rel, "prop": {"type": "remove"}},
                    {"name": obj, "type": "remove", "prop": {}}
                ]
            )
        return triplets_to_remove
        
    @staticmethod
    def parse_replacements_thesis(raw_replacements):
        raw_replacements = raw_replacements.lower()
        predicted_outdated = raw_replacements.split("[")[-1].split("]")[0].split(";")
        predicted_outdated = [pair.strip().split("<-")[1].strip(''' \n'".,/''') for pair in predicted_outdated if "<-" in pair]
        triplets_to_remove = []
        for outdated_thesis in predicted_outdated:
            triplets_to_remove.append(
                [
                    {"name": "remove", "type": "remove", "prop": {}},
                    {"name": "hyper", "prop": {"type": "hyper"}},
                    {"name": outdated_thesis, "type": "hyper", "prop": {}}
                ]
            )
        return triplets_to_remove
    
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
    def stringify(triplet):
        if triplet[1]["prop"]["type"] in ["hyper", "episodic"]:
            return triplet[1]["prop"]["time"] + ": " + triplet[2]["name"]
        if triplet[1]["prop"]["type"] in ["simple"]:
            return triplet[1]["prop"]["time"] + ": " + " ".join([triplet[0]["name"], triplet[1]["name"], triplet[2]["name"]])
        
    @staticmethod    
    def stringify_all(triplets):
        return list({LLMUpdator.stringify(triplet) for triplet in triplets}) 
