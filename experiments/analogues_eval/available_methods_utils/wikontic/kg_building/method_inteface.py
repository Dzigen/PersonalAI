from typing import List, Dict
import yaml
from tqdm import tqdm
import sys

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGBuildOperations
from analogues_eval.available_methods_utils.wikontic.utils import CustomWikontic, create_id

class WikonticBuildOperations(GraphRAGBuildOperations):
    def __init__(self, config: Dict):
        CustomWikontic.init_graph(config)

        self.method = CustomWikontic(config)
        self.config = config

    @staticmethod
    def prepare_method_config(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> Dict:

        llm_info = hyperp_params['METHOD_CONFIG']['agent_config']
        llm_base_url = f"http://{llm_info['credentials']['host']}:{llm_info['credentials']['port']}/v1"
        embedder_info = hyperp_params['METHOD_CONFIG']['embedder_config']

        base_kg_path = f"{env_params['WORKSPACE_CONTAINER_DIRS']['base_path']}/{env_params['WORKSPACE_CONTAINER_DIRS']['kg']}"
        save_dir = f"{base_kg_path}/{hyperp_params['METHOD_NAME']}/{hyperp_params['DATASET_NAME']}/{hyperp_params['KNOWLEDGE_GRAPH_NAME']}"

        config = {
            'mongo_uri': f"mongodb://{conn_params['KG_MODEL_CONNECTORS']['host']}:{conn_params['KG_MODEL_CONNECTORS']['port']}/?directConnection=true",
            'save_dir': save_dir,
            'llm_model_name': llm_info['credentials']['model'],
            'llm_base_url': llm_base_url,
            'embedding_model_name': embedder_info['model_name_or_path'],
            'wikidata_ontology_db': conn_params['KG_MODEL_CONNECTORS']['wikidata_ontology_db'],
            'db_onto': conn_params['KG_MODEL_CONNECTORS']['db_onto']
        }
        return config

    def build_graph(self, documents: List[str]) -> None:
        for document in tqdm(documents):
            self.method.inferer.extract_triplets_with_ontology_filtering_and_add_to_db(
                text=document, sample_id=create_id()
            )

    def save_graph(self, env_params: Dict, hyperp_params: Dict) -> None:
        pass

    def print_graph_info(self) -> None:
        pass

    @staticmethod
    def prepare_kgbuild_env_params(conn_params: Dict, env_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        DATASET_KGS_PATH = f"{env_params['LOCAL_KG_PATH']}/{hyperp_params['METHOD_NAME']}/{hyperp_params['DATASET_NAME']}"
        SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{hyperp_params['KNOWLEDGE_GRAPH_NAME']}"
        MONGO_VOLUME_PATH = f"{SPEC_KG_PATH}/{env_params['KG_DIR_STRUCT']['storage']}"

        mongo_cnt_variables = {
            'MONGO_CNTNAME': conn_params['CONTAINERS_ADDITIONAL_CONFIG']['mongo_cntname'],
            'MONGO_EXTERNAL_PORT': conn_params['KG_MODEL_CONNECTORS']['port'],
            'MONGO_LOCAL_VOLUME': MONGO_VOLUME_PATH,
            'MONGO_HOST': conn_params['CONTAINERS_ADDITIONAL_CONFIG']['mongo_host']
        }
        return [mongo_cnt_variables]


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
    env_params = WikonticBuildOperations.prepare_kgbuild_env_params(
        example_conn_params, example_env_params, example_hyperp_params)
    print(env_params)

    print("Generated config:")
    config = WikonticBuildOperations.prepare_method_config(
        example_conn_params, example_env_params, example_hyperp_params)
    print(config)

    print("Initializing method...")
    method = WikonticBuildOperations(config)
    print("Building graph...")
    method.build_graph(example_documents)

    print("Builded graph info:")
    method.print_graph_info()
    print("Saving graph...")
    method.save_graph()
    print("Done!")
