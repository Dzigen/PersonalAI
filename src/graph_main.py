import ast

from src.neo4j_functions import Neo4jConnection
from src.embedding_functions import EmbeddingDatabaseConnection
from src.agents.private import GigaChatAgent
from src.prompts.extraction_prompts import \
    triplet_extraction_prompt, thesis_extraction_prompt
from src.prompts.replacements_prompts import \
    replace_simple_prompt, replace_thesis_prompt
from src.utils import Logger
from src.retrieve.retriever import Retriever

from .qa_pipeline import QAPipeline, QAPipelineConfig
from .knowledge_graph_model import KnowledgeGraphModel

class RemoteKnowledgeGraph:
    def __init__(self, uri, user, pwd, db_name, logpath, pipeline = None, retriever_device = "cpu", some_other_params = None):
        self.conn = Neo4jConnection(uri, user, pwd)
        self.agent = LLaMAagent("You are a helpful assistant", pipeline)
        self.log = Logger(logpath)
        self.db_name = db_name
        self.embedder = Retriever(device=retriever_device)
        self.emb_conn = EmbeddingDatabaseConnection(some_other_params)

        # TODO
        #self.kg_model = KnowledgeGraphModel()
        #self.llm_agent = LLaMAagent("You are a helpful assistant", pipeline)
        #self.qa_pipeline = QAPipeline(self.kg_model, self.llm_agent)
        #self.updatekg_pipeline = UpdateKGPipeline()

    @staticmethod            
    def stringify(triplet):
        if triplet[1]["prop"]["type"] in ["hyper", "episodic"]:
            return triplet[1]["prop"]["time"] + ": " + triplet[2]["name"]
        if triplet[1]["prop"]["type"] in ["simple"]:
            return triplet[1]["prop"]["time"] + ": " + " ".join([triplet[0]["name"], triplet[1]["name"], triplet[2]["name"]])
        
    @staticmethod    
    def stringify_all(triplets):
        return list({RemoteKnowledgeGraph.stringify(triplet) for triplet in triplets})                
        
    def extract_triplets(self, text, node_prop = {}, rel_prop = {}):
        raw_response = self.agent.generate(triplet_extraction_prompt.format(text))
        self.log("TEXT: " + text)
        self.log("EXTRACTED TRIPLETS: " + str(raw_response))
        new_triplets = self.parse_triplets(raw_response, node_prop, rel_prop)
        return new_triplets
        
    def extract_thesises(self, text, node_prop = {}, rel_prop = {}):
        raw_response = self.agent.generate(thesis_extraction_prompt.format(text = text))
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
    
    def update(self, new_triplets, replacing_window_width, replacing_window_depth, need_simple = True, need_thesises = True):
        assert need_simple or need_thesises
        entities = self.get_entities_from_triplets(new_triplets)  
        triplets_to_remove = []  
        
        if need_simple:    
            ex_triplets = self.bfs(entities, replacing_window_depth, edge_types = ["simple"], max_triplets = replacing_window_width, some_other_params=None)
            if ex_triplets:
                replacements = self.agent.generate(replace_simple_prompt.format(ex_triplets = self.stringify_all(ex_triplets), 
                                                                        new_triplets = self.stringify_all(new_triplets)))
                self.log("FOUND SIMPLE REPLACEMENTS: " + str(replacements))
                triplets_to_remove += self.parse_replacements_simple(replacements)
            else:
                self.log("FOUND NO EXISTED SIMPLE TRIPLETS TO REMOVE")
            
        if need_thesises:    
            ex_triplets = self.bfs(entities, replacing_window_depth, edge_types = ["hyper"], max_triplets = replacing_window_width, some_other_params=None)
            if ex_triplets:
                replacements = self.agent.generate(replace_thesis_prompt.format(ex_triplets = self.stringify_all(ex_triplets), 
                                                                        new_triplets = self.stringify_all(new_triplets)))
                self.log("FOUND THESIS REPLACEMENTS: " + str(replacements))
                triplets_to_remove += self.parse_replacements_thesis(replacements)
            else:
                self.log("FOUND NO EXISTED THESIS TRIPLETS TO REMOVE")
            
        return triplets_to_remove
    
    def bfs(self, entities, depth, edge_types, max_triplets, some_other_params = None):
        # TODO
        pass
    
    def a_star(self, entities, depth, edge_types, max_triplets, some_other_params = None):
        # TODO
        pass
    
    def remember(self, text, replacing_window_width = 32, replacing_window_depth = 1, need_simple = True, need_thesises = True, need_episodic = True, 
                 need_update = False, node_prop = {}, rel_prop = {}):
        assert need_simple or need_thesises
        new_triplets = []
        if need_simple:
            new_simple_triplets = self.extract_triplets(text, node_prop, rel_prop)
            new_triplets += new_simple_triplets
        if need_thesises:
            new_thesises_triplets = self.extract_thesises(text, node_prop, rel_prop)
            new_triplets += new_thesises_triplets
            
        if need_update:
            triplets_to_remove = self.update(new_triplets, replacing_window_width, replacing_window_depth, need_simple, need_thesises)
        
        if need_episodic:
            new_triplets += self.get_episodic_relationships(text, self.get_entities_from_triplets(new_triplets))
            
        self.add_triplets(new_triplets)
        if need_update:
            self.delete_triplets(triplets_to_remove)
      
    # TO MODIFY 
    # We can't extract too large graph via connection, but we can
    # generate some condition for bfs and A*. We need a brainshtorm for this method later   
    def retrieve(self, query, bfs_depth, a_star_depth, edge_types, max_triplets, some_other_params = None):
        key_entities = self.extract_key_entities(query, some_other_params = None)
        sypher_query = self.generate_sypher_query(query, some_other_params = None)
        selected_triplets = None
        if sypher_query is not None:
            selected_triplets = self.conn.extract_triplets_by_query(sypher_query, max_triplets)
            
        if selected_triplets is None:
            bfs_triplets = self.bfs(key_entities, bfs_depth, edge_types, max_triplets = int(max_triplets / 2), some_other_params=None)
            a_star_triplets = self.a_star(key_entities, a_star_depth, edge_types, max_triplets = int(max_triplets / 2), some_other_params=None)
            selected_triplets = bfs_triplets + [triplet for triplet in a_star_triplets if triplet not in bfs_triplets]
        
        selected_triplets = self.stringify_all(selected_triplets)
        self.log("RETRIEVED TRIPLETS: " + str(selected_triplets))
        return selected_triplets
    
    @staticmethod
    def parse_thesises(response, node_prop, rel_prop):
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
    def parse_triplets(raw_triplets, node_prop, rel_prop):
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
    def get_episodic_relationships(text, entities, node_prop, rel_prop):
        episodic_triplets = []
        for entity in entities:
            triplet = [entity, {"name": "episodic", "prop": {"type": "episodic", **rel_prop}}, 
                       {"name": text, "type": "episodic_node", "prop": {**node_prop}}]
            episodic_triplets.append(triplet)
            
        return episodic_triplets
    
    def add_triplets(self, triplets):
        self.emb_conn.add_triplets(triplets)
        self.conn.create_triplets(triplets)
        
    def delete_triplets(self, triplets):
        deleted_entities = self.conn.delete_triplets(triplets)
        self.emb_conn.delete_triplets(triplets, deleted_entities)
                
    def extract_key_entities(self, query, some_other_params = None):
        # TODO
        pass
    
    def generate_sypher_query(self, query, some_other_params = None):
        # TODO
        pass
            
        
        
                
        
        
    
        
        

