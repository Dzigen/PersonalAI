from typing import List, Dict, Union
import yaml
from tqdm import tqdm
import os
import json
import sys

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGBuildOperations


class KGGenBuildOperations(GraphRAGBuildOperations):
    def __init__(self, config: Dict):
        from kg_gen import KGGen, Graph # костыль

        self.method: KGGen = KGGen(
            model=config['llm_model_name'],
            temperature=config['temperature'],
            reasoning_effort=config['reasoning_effort'],
            max_tokens=config['max_tokens'],
            api_base=config['llm_base_url'],
            retrieval_model=config['embedding_model_name']
        )
        self.config: Dict = config
        self.aggregated_graph: Union[None, Graph] = None

    @staticmethod
    def prepare_method_config(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> Dict:
        llm_info = hyperp_params['METHOD_CONFIG']['agent_config']
        llm_base_url = f"http://{llm_info['credentials']['host']}:{llm_info['credentials']['port']}"
        embedder_info = hyperp_params['METHOD_CONFIG']['embedder_config']

        base_kg_path = f"{env_params['WORKSPACE_CONTAINER_DIRS']['base_path']}/{env_params['WORKSPACE_CONTAINER_DIRS']['kg']}"
        save_dir = f"{base_kg_path}/{hyperp_params['METHOD_NAME']}/{hyperp_params['DATASET_NAME']}/{hyperp_params['KNOWLEDGE_GRAPH_NAME']}"

        config = {
            'save_dir': save_dir,
            'llm_model_name': f"{llm_info['vendor']}/{llm_info['credentials']['model']}",
            'llm_base_url': llm_base_url,
            'embedding_model_name': embedder_info['model_name_or_path'],
            'temperature': 0.0,
            'reasoning_effort':None,
            'max_tokens':16000,
            'cluster': True
        }
        return config

    def build_graph(self, documents: List[str]) -> None:
        import pydantic_core
        occured_error_counter = 0

        print("Start separate graphs creation...")
        graphs: List[Graph] = list()
        for i, document in enumerate(tqdm(documents)):
            try:
                graph = self.method.generate(input_data=document, cluster=self.config['cluster'])
                graphs.append(graph)
            except pydantic_core._pydantic_core.ValidationError:
                print(f"error occurs during text storing to knowledge graph; text idx: {i}")
                occured_error_counter += 1

        print("Separate graphs are built!")
        print(f"Occurred errors statistic: {occured_error_counter} / {len(documents)}")

        print("Start graphs aggregation...")
        self.aggregated_graph: Graph = self.method.aggregate(graphs)
        print("Graphs are aggregated!")

    def save_graph(self, env_params: Dict, hyperp_params: Dict) -> None:
        os.makedirs(self.config['save_dir'], exist_ok=True)
        output_path = os.path.join(self.config['save_dir'], "graph.json")

        graph_dict = {
            "entities": list(self.aggregated_graph.entities),
            "relations": list(self.aggregated_graph.relations),
            "edges": list(self.aggregated_graph.edges),
            "entity_clusters": {
                k: list(v) for k, v in self.aggregated_graph.entity_clusters.items()
            }
            if self.aggregated_graph.entity_clusters
            else None,
            "edge_clusters": {k: list(v) for k, v in self.aggregated_graph.edge_clusters.items()}
            if self.aggregated_graph.edge_clusters
            else None,
        }

        with open(output_path, "w") as f:
            json.dump(graph_dict, f, indent=2)

    def print_graph_info(self) -> None:
        try:
            self.method.visualize(self.aggregated_graph, f"{self.config['save_dir']}/graph-visualization.html", open_in_browser=False)
        except ValueError:
            pass

    @staticmethod
    def prepare_kgbuild_env_params(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        return []
    
    @staticmethod
    def create_kg_structure(env_params: Dict, hyperp_params: Dict) -> None:
        pass

if __name__ == "__main__":

    kgconnparams_path = "./debug/example/kgconn_params.yaml"  # TO CHANGE
    with open(kgconnparams_path, 'r') as stream:
        example_conn_params = yaml.safe_load(stream)

    envparams_path = "./debug/example/kgenv_params.yaml" # TO CHANGE
    with open(envparams_path, 'r') as stream:
        example_env_params = yaml.safe_load(stream)

    hyperpparams_path = "./debug/example/kghyperp_params.yaml"  # TO CHANGE
    with open(hyperpparams_path, 'r') as stream:
        example_hyperp_params = yaml.safe_load(stream)

    example_documents = [
        "Oliver Badman is a politician.",
        "George Rankin is a politician.",
        "Thomas Marwick is a politician.",
        "Cinderella attended the royal ball.",
        "The prince used the lost glass slipper to search the kingdom.",
        "When the slipper fit perfectly, Cinderella was reunited with the prince.",
        "Erik Hort's birthplace is Montebello.",
        "Marina is bom in Minsk.",
        "Montebello is a part of Rockland County."
    ]

    print("Generated env params:")
    env_params = KGGenBuildOperations.prepare_kgbuild_env_params(
        example_conn_params, example_env_params, example_hyperp_params)
    print(env_params)

    print("Generated config:")
    config = KGGenBuildOperations.prepare_method_config(
        example_conn_params, example_env_params, example_hyperp_params)
    print(config)

    print("Generating method-graph structure:")
    KGGenBuildOperations.create_kg_structure(
        example_env_params, example_hyperp_params)

    print("Initializing method...")
    method = KGGenBuildOperations(config)
    print("Building graph...")
    method.build_graph(example_documents)

    print("Builded graph info:")
    method.print_graph_info()
    print("Saving graph...")
    method.save_graph(example_env_params, example_hyperp_params)
    print("Done!")
