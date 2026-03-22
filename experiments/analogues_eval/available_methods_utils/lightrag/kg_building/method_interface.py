import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

from typing import List, Dict
import sys
import yaml
import os
import asyncio
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

EXPERIMENTS_BASE_PATH="/home/workspace/experiments" # TO CHANGE
sys.path.insert(0, EXPERIMENTS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGBuildOperations

HF_TOKEN = None # TO CHANGE

class LightRAGBuildOperations(GraphRAGBuildOperations):
    def __init__(self, config: Dict):
        # костыль
        LIGHTRAG_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/lightrag/method_source"  # TO CHANGE
        sys.path.insert(0, LIGHTRAG_SOURCE_PATH)

        from lightrag.utils import setup_logger
        from lightrag import LightRAG
        from lightrag.llm.openai import openai_complete_if_cache
        from lightrag.utils import EmbeddingFunc
        setup_logger("lightrag", level="INFO")

        async def ollama_complete_func(
                prompt, system_prompt=None, history_messages=None, enable_cot: bool = False,
                keyword_extraction=False, **kwargs) -> str:
            if history_messages is None:
                history_messages = []
            return await openai_complete_if_cache(
                config['llm_model_name'],
                prompt,
                api_key='ollama',
                system_prompt=system_prompt,
                history_messages=history_messages,
                enable_cot=enable_cot,
                keyword_extraction=keyword_extraction,
                **kwargs,
            )

        self.embedder_model = SentenceTransformer(config['embedding_model_name'], token=HF_TOKEN)

        async def embedding_func(texts: list[str]) -> np.ndarray:
            embeddings = self.embedder_model.encode(texts, convert_to_numpy=True)
            return embeddings

        if not os.path.exists(config['save_dir']):
            os.mkdir(config['save_dir'])

        self.method = LightRAG(
            working_dir=config['save_dir'],
            embedding_func=EmbeddingFunc(
                embedding_dim=config['embedding_dim'],
                max_token_size=config['embedding_max_token_size'],
                func=embedding_func,
            ),
            llm_model_func=ollama_complete_func,
            llm_model_kwargs={"base_url": config['llm_base_url'], "max_completion_tokens": 32768, 'timeout': 60},
            llm_model_name=config['llm_model_name']
        )
        asyncio.run(self.method.initialize_storages())

        self.config = config

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

            'embedding_model_name': embedder_info['model_name_or_path'],
            'embedding_dim': 1024,
            'embedding_max_token_size': 8192
        }
        return config

    def build_graph(self, documents: List[str]) -> None:
        asyncio.run(self.method.ainsert(input=documents))

    def save_graph(self, env_params: Dict, hyperp_params: Dict) -> None:
        pass

    def print_graph_info(self) -> None:
        pass

    def prepare_kgbuild_env_params(self, conn_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        return []

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
    env_params = LightRAGBuildOperations.prepare_kgbuild_env_params(
        example_conn_params, example_env_params, example_hyperp_params)
    print(env_params)

    print("Generated config:")
    config = LightRAGBuildOperations.prepare_method_config(
        example_conn_params, example_env_params, example_hyperp_params)
    print(config)

    print("Generating method-graph structure:")
    LightRAGBuildOperations.create_kg_structure(
        example_env_params, example_hyperp_params)

    print("Initializing method...")
    method = LightRAGBuildOperations(config)
    print("Building graph...")
    method.build_graph(example_documents)

    print("Builded graph info:")
    method.print_graph_info()
    print("Saving graph...")
    method.save_graph(example_env_params, example_hyperp_params)
    print("Done!")
