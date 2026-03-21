import sys
import yaml
from tqdm import tqdm
from typing import List, Dict

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)
from analogues_eval.available_methods_utils.utils import GraphRAGBuildOperations


class RaptorBuildOperations(GraphRAGBuildOperations):
    def __init__(self, config: Dict):
        # костыль
        RAPTOR_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/raptor/method_source"  # TO CHANGE
        sys.path.insert(0, RAPTOR_SOURCE_PATH)
        from raptor import RetrievalAugmentation, RetrievalAugmentationConfig, SBertEmbeddingModel

        UTILS_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/raptor"  # TO CHANGE
        sys.path.insert(0, UTILS_SOURCE_PATH)
        from utils import CustomQAModel, CustomSummarizationModel

        formated_config = RetrievalAugmentationConfig(
            summarization_model=CustomSummarizationModel(
                model_name=config['llm_model_name'], base_url=config['llm_base_url']
            ),
            qa_model=CustomQAModel(
                model_name=config['llm_model_name'], base_url=config['llm_base_url']
            ),
            embedding_model=SBertEmbeddingModel(
                model_name=config['embedding_model_name']
            )
        )
        self.method = RetrievalAugmentation(config=formated_config)
        self.config = config

    @staticmethod
    def prepare_method_config(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> Dict:

        llm_info = hyperp_params['METHOD_CONFIG']['agent_config']
        llm_base_url = f"http://{llm_info['credentials']['host']}:{llm_info['credentials']['port']}/v1"
        embedder_info = hyperp_params['METHOD_CONFIG']['embedder_config']

        base_kg_path = f"{env_params['WORKSPACE_CONTAINER_DIRS']['base_path']}/{env_params['WORKSPACE_CONTAINER_DIRS']['kg']}"
        save_dir = f"{base_kg_path}/{hyperp_params['METHOD_NAME']}/{hyperp_params['DATASET_NAME']}/{hyperp_params['KNOWLEDGE_GRAPH_NAME']}"

        config = {
            'save_dir': save_dir,
            'llm_model_name': llm_info['credentials']['model'],
            'llm_base_url': llm_base_url,
            'embedding_model_name': embedder_info['model_name_or_path']
        }
        return config

    def build_graph(self, documents: List[str]) -> None:
        concated_documents = '\n\n'.join(documents)
        self.method.add_documents(concated_documents)

    def save_graph(self, env_params: Dict, hyperp_params: Dict) -> None:
        self.method.save(f"{self.config['save_dir']}/storage")

    def print_graph_info(self) -> None:
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
    env_params = RaptorBuildOperations.prepare_kgbuild_env_params(
        example_conn_params, example_env_params, example_hyperp_params)
    print(env_params)

    print("Generated config:")
    config = RaptorBuildOperations.prepare_method_config(
        example_conn_params, example_env_params, example_hyperp_params)
    print(config)

    print("Generating method-graph structure:")
    RaptorBuildOperations.create_kg_structure(
        example_env_params, example_hyperp_params)

    print("Initializing method...")
    method = RaptorBuildOperations(config)
    print("Building graph...")
    method.build_graph(example_documents)

    print("Builded graph info:")
    method.print_graph_info()
    print("Saving graph...")
    method.save_graph(example_env_params, example_hyperp_params)
    print("Done!")
