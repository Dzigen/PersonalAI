from typing import Dict, List, Union
from time import time
import openai
import hashlib
import gc
import logging

def create_id(seed: Union[None, str] = None) -> str:
    if seed is None:
        seed = f"{time()}"
    return hashlib.md5(seed.encode()).hexdigest()

def get_mongo_client(mongo_uri):
    from pymongo.mongo_client import MongoClient
    client = MongoClient(mongo_uri)
    return client

class CustomWikontic:

    def __init__(self, config: Dict):
        # костыль
        from wikontic.create_wikidata_ontology_db import create_wikidata_ontology_database
        from wikontic.create_ontological_triplets_db import (
            create_ontological_triplets_database,
        )
        from wikontic.utils.structured_inference_with_db import StructuredInferenceWithDB
        from wikontic.utils.structured_aligner import Aligner
        from wikontic.utils.openai_utils import LLMTripletExtractor, logger

        # !! PAY ATTENTION !!!
        #logger.setLevel(logging.DEBUG) 

        mongo_client = get_mongo_client(config['mongo_uri'])
        triplets_db = mongo_client.get_database("test_db_onto")
        ontology_db = mongo_client.get_database("wikidata_ontology_test")

        self.aligner = Aligner(triplets_db=triplets_db, ontology_db=ontology_db)
        self.extractor = LLMTripletExtractor(api_key="ollama")

        # костыль: подключаемся к ollama-контейнеру
        self.extractor.model = config['llm_model_name']
        del self.extractor.client
        gc.collect()
        self.extractor.client = openai.OpenAI(api_key="ollama", base_url=config['llm_base_url'], timeout=600)
        messages = [
            {"role": "system", "content": "You are a helpfull assistant"},
            {"role": "user", "content": "What is 2+2?"},
        ]
        response = self.extractor.client.chat.completions.create(
            model=self.extractor.model, messages=messages, temperature=0
        )
        print(f"Ollama connecttion check; ping output:\n{response.choices[0].message.content}\n===")

        self.inferer = StructuredInferenceWithDB(self.extractor, self.aligner, triplets_db)

    @staticmethod
    def init_graph(config: Dict):
        # костыль
        from wikontic.create_wikidata_ontology_db import create_wikidata_ontology_database
        from wikontic.create_ontological_triplets_db import (
            create_ontological_triplets_database,
        )
        from wikontic.utils.structured_inference_with_db import StructuredInferenceWithDB
        from wikontic.utils.structured_aligner import Aligner
        from wikontic.utils.openai_utils import LLMTripletExtractor, logger

        create_wikidata_ontology_database(
            mongo_uri=config['mongo_uri'],
            database=config['wikidata_ontology_db']
        )

        create_ontological_triplets_database(
            mongo_uri=config['mongo_uri'],
            db_name=config['db_onto']
        )
