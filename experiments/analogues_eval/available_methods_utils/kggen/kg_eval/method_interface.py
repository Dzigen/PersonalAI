from typing import Dict, List
import yaml
import sys
import json

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)
from analogues_eval.available_methods_utils.utils import GraphRAGMINEOperations

class KGGenMINEOperations(GraphRAGMINEOperations):

    def __init__(self, memory_config: Dict, mine_config: Dict) -> None:
        from kg_gen import KGGen, Graph # костыль

        self.method: KGGen = KGGen(
            model=memory_config['llm_model_name'],
            temperature=memory_config['temperature'],
            reasoning_effort=memory_config['reasoning_effort'],
            max_tokens=memory_config['max_tokens'],
            api_base=memory_config['llm_base_url'],
            retrieval_model=memory_config['embedding_model_name']
        )
        self.memory_config: Dict = memory_config
        self.mine_config = mine_config
        self.aggregated_graph: Graph = self.method.from_file(f"{memory_config['save_dir']}/graph.json")
        #print(self.aggregated_graph)

        self.aggregated_nxgraph = KGGen.to_nx(self.aggregated_graph)
        #print(self.aggregated_nxgraph)

        self.node_embeddings, _ = self.method.generate_embeddings(self.aggregated_nxgraph)

    def get_neighbour_triples(self, question: str) -> List[str]:
        _, context, _ = self.method.retrieve(
            question, self.node_embeddings, self.aggregated_nxgraph,
            k=self.mine_config['max_init_nodes'])
        
        filtered_context = list(context)
        if self.mine_config['triples_in_total'] > 0:
            filtered_context = filtered_context[:self.mine_config['triples_in_total']]
        
        return filtered_context

    @staticmethod
    def prepare_mine_config() -> Dict:
        return {
            "max_init_nodes": 8, "max_depth": 2,
            #"nodes_per_depth": 4, "triples_per_node": 4,
            "triples_in_total": 64
        }

    @staticmethod
    def prepare_kgeval_mine_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        return list()

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

    print("Method config:")
    print(example_memory_config)

    print("Generated env params:")
    env_params = KGGenMINEOperations.prepare_kgeval_mine_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated mine config:")
    mine_config = KGGenMINEOperations.prepare_mine_config()
    print(mine_config)

    queries = [
        "What is George Rankin's occupation?",
        "How did Cinderella reach her happy ending?",
        "What county is Erik Hort's birthplace a part of?"
    ]

    print("Initializing method...")
    method = KGGenMINEOperations(example_memory_config, mine_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing MINE retrieval...")
    for query in queries:
        retrieved_triples = method.get_neighbour_triples(query)
        print(f"query: {query}")
        print(f"retrieved triples ({len(retrieved_triples)}): {retrieved_triples}")

    print("Done!")
