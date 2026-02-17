from typing import Dict, List, Union
from pymongo.mongo_client import MongoClient
from time import time
import hashlib

from wikontic.create_wikidata_ontology_db import create_wikidata_ontology_database
from wikontic.create_ontological_triplets_db import (
    create_ontological_triplets_database,
)
from wikontic.utils.structured_inference_with_db import StructuredInferenceWithDB
from wikontic.utils.structured_aligner import Aligner
from wikontic.utils.openai_utils import LLMTripletExtractor

def create_id(seed: Union[None, str] = None) -> str:
    if seed is None:
        seed = f"{time()}"
    return hashlib.md5(seed.encode()).hexdigest()

def get_mongo_client(mongo_uri):
    client = MongoClient(mongo_uri)
    return client

class CustomWikontic:

    def __init__(self, config: Dict):
        mongo_client = get_mongo_client(config['mongo_uri'])
        triplets_db = mongo_client.get_database("test_db_onto")
        ontology_db = mongo_client.get_database("wikidata_ontology_test")

        self.aligner = Aligner(triplets_db=triplets_db, ontology_db=ontology_db)
        self.extractor = LLMTripletExtractor(model="gpt-4o", api_key=api_key, proxy=proxy_url)
        self.inferer = StructuredInferenceWithDB(self.extractor, self.aligner, triplets_db)

    @staticmethod
    def init_graph(self, config: Dict):
        create_wikidata_ontology_database(
            mongo_uri=config['mongo_uri'],
            database=config['wikidata_ontology_db']
        )

        create_ontological_triplets_database(
            mongo_uri=config['mongo_uri'],
            db_name=config['db_onto']
        )
