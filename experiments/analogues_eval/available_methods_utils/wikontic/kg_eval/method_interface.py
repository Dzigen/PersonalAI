from typing import Dict, List
import yaml
import sys
import json

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGMINEOperations
from analogues_eval.available_methods_utils.wikontic.utils import CustomWikontic
from analogues_eval.available_methods_utils.wikontic.kg_building import WikonticBuildOperations

class WikonticMINEOperations(GraphRAGMINEOperations, WikonticBuildOperations):

    def __init__(self, memory_config: Dict, mine_config: Dict) -> None:
        self.method = CustomWikontic(memory_config)
        self.config = memory_config
        self.mine_config = mine_config

    def get_neighbour_triples(self, question: str) -> List[str]:
        ents = self.method.inferer.identify_relevant_entities_from_question_with_llm(question)
        supporting_triplets, _ = self.method.inferer.answer_question_with_llm(question, linked_entities=ents)

        triples = [f"{triple['subject']} {triple['relation']} {triple['object']}" for triple in supporting_triplets]

        filtered_triples = list(triples)
        if self.mine_config['triples_in_total'] > 0:
            filtered_triples = filtered_triples[:self.mine_config['triples_in_total']]
        
        return filtered_triples

    @staticmethod
    def prepare_mine_config() -> Dict:
        return {
            "max_init_nodes": 8, "max_depth": 2#,
            #"nodes_per_depth": 4, "triples_per_node": 4,
            #"triples_in_total": 64
        }

    @staticmethod
    def prepare_kgeval_mine_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        DATASET_KGS_PATH = f"{env_params['LOCAL_KG_PATH']}/{env_params['METHOD_NAME']}/{env_params['DATASET_NAME']}"
        SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{env_params['KNOWLEDGE_GRAPH_NAME']}"
        MONGO_EXTERNAL_DB_VOLUME = f"{SPEC_KG_PATH}/{env_params['KG_DIR_STRUCT']['db_storage']}"
        MONGO_EXTERNAL_CONFIGDB_VOLUME = f"{SPEC_KG_PATH}/{env_params['KG_DIR_STRUCT']['configdb_storage']}"
        MONGO_EXTERNAL_MONGOT_VOLUME = f"{SPEC_KG_PATH}/{env_params['KG_DIR_STRUCT']['mongot_storage']}"

        mongo_cnt_variables = {
            'MONGO_CNTNAME': env_params['CONTAINERS_ADDITIONAL_CONFIG']['mongo_cntname'],
            'MONGO_HOST': conn_params['CONTAINERS_ADDITIONAL_CONFIG']['mongo_host'],
            'MONGO_EXTERNAL_PORT': conn_params['KG_MODEL_CONNECTORS']['port'],
            'MONGO_EXTERNAL_DB_VOLUME': MONGO_EXTERNAL_DB_VOLUME,
            'MONGO_EXTERNAL_CONFIGDB_VOLUME': MONGO_EXTERNAL_CONFIGDB_VOLUME,
            'MONGO_EXTERNAL_MONGOT_VOLUME': MONGO_EXTERNAL_MONGOT_VOLUME
        }
        return [mongo_cnt_variables]

if __name__ == "__main__":

    kgconnparams_path = "./debug/example/kgconn_params.yaml"  # TO CHANGE
    with open(kgconnparams_path, 'r') as stream:
        example_kgconn_params = yaml.safe_load(stream)

    envparams_path = "./debug/example/kgevalenv_params.yaml" # TO CHANGE
    with open(envparams_path, 'r') as stream:
        example_env_params = yaml.safe_load(stream)

    memoryconfig_path = "./debug/example/kg_config"  # TO CHANGE
    with open(memoryconfig_path, 'r', encoding='utf-8') as fd:
        example_memory_config = json.loads(fd.read())

    print("Generated env params:")
    env_params = WikonticMINEOperations.prepare_kgeval_mine_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated mine config:")
    mine_config = WikonticMINEOperations.prepare_mine_config()
    print(mine_config)


    queries = [
        "What is George Rankin's occupation?",
        "How did Cinderella reach her happy ending?",
        "What county is Erik Hort's birthplace a part of?"
    ]

    print("Initializing method...")
    method = WikonticMINEOperations(example_memory_config, mine_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing MINE retrieval...")
    for query in queries:
        retrieved_triples = method.get_neighbour_triples(query)
        print(f"query: {query}")
        print(f"retrieved triples ({len(retrieved_triples)}): {retrieved_triples}")

    print("Done!")
