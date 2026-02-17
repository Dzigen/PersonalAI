from typing import Dict, List
import yaml
from ...utils import GraphRAGMINEOperations
from ..utils import CustomWikontic

class WikonticMINEOperations(GraphRAGMINEOperations):

    def __init__(self, memory_config: Dict, mine_config: Dict) -> None:
        self.method = CustomWikontic(memory_config)
        self.config = memory_config
        self.mine_config = mine_config

    def get_neighbour_triples(self, question: str) -> List[str]:
        ents = self.method.inferer.identify_relevant_entities_from_question_with_llm(question)
        supporting_triplets, _ = self.method.inferer.answer_question_with_llm(question, linked_entities=ents)

        triples = [f"{triple['subject']} {triple['relation']} {triple['object']}" for triple in supporting_triplets]

        return triples

    @staticmethod
    def prepare_mine_config() -> Dict:
        return {
            "max_init_nodes": 8, "max_depth": 2#,
            #"nodes_per_depth": 4, "triples_per_node": 4,
            #"triples_in_total": 64
        }

    @staticmethod
    def prepare_kgeval_mine_env_params(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        DATASET_KGS_PATH = f"{env_params['BASE_KG_PATH']}/{env_params['METHOD_NAME']}/{env_params['DATASET_NAME']}"
        SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{env_params['KNOWLEDGE_GRAPH_NAME']}"
        MONGO_VOLUME_PATH = f"{SPEC_KG_PATH}/{env_params['KG_DIR_STRUCT']['storage']}"

        mongo_cnt_variables = {
            'MONGO_CNTNAME': conn_params['CONTAINERS_ADDITIONAL_CONFIG']['mongo_cntname'],
            'MONGO_EXTERNAL_PORT': conn_params['KG_MODEL_CONNECTORS']['port'],
            'MONGO_LOCAL_VOLUME': MONGO_VOLUME_PATH
        }
        return [mongo_cnt_variables]

if __name__ == "__main__":

    kgconnparams_path = "./debug/example/kgconn_params.yaml"  # TO CHANGE
    with open(kgconnparams_path, 'r') as stream:
        example_kgconn_params = yaml.safe_load(stream)

    envparams_path = "./debug/example/kgevalenv_params.yaml" # TO CHANGE
    with open(envparams_path, 'r') as stream:
        example_env_params = yaml.safe_load(stream)

    memoryconfig_path = "./debug/example/kg_config.yaml"  # TO CHANGE
    with open(memoryconfig_path, 'r') as stream:
        example_memory_config = yaml.safe_load(stream)


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
    method = WikonticMINEOperations(example_memory_config, example_memory_config, mine_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing MINE retrieval...")
    for query in queries:
        retrieved_triples = method.get_neighbour_triples(query)
        print(f"query: {query}")
        print(f"retrieved triples ({len(retrieved_triples)}): {retrieved_triples}")

    print("Done!")
