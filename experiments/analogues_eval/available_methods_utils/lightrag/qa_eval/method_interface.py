import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
import yaml
from typing import List, Dict
import sys
import json
import yaml
import asyncio
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer


EXPERIMENTS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPERIMENTS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGQAOperations
from analogues_eval.available_methods_utils.lightrag.kg_building import LightRAGBuildOperations

HF_TOKEN = None # TO CHANGE

class LightRAGQAOperations(GraphRAGQAOperations, LightRAGBuildOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict):
        # костыль
        LIGHTRAG_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/lightrag/method_source"  # TO CHANGE
        sys.path.insert(0, LIGHTRAG_SOURCE_PATH)

        from lightrag.utils import setup_logger
        from lightrag import LightRAG, QueryParam
        from lightrag.llm.openai import openai_complete_if_cache
        from lightrag.utils import EmbeddingFunc
        setup_logger("lightrag", level="WARNING")

        async def ollama_complete_func(
                prompt, system_prompt=None, history_messages=None, enable_cot: bool = False,
                keyword_extraction=False, **kwargs) -> str:
            if history_messages is None:
                history_messages = []
            return await openai_complete_if_cache(
                memory_config['llm_model_name'],
                prompt,
                api_key='ollama',
                system_prompt=system_prompt,
                history_messages=history_messages,
                enable_cot=enable_cot,
                keyword_extraction=keyword_extraction,
                **kwargs,
            )

        async def embedding_func(texts: list[str]) -> np.ndarray:
            model = SentenceTransformer(memory_config['embedding_model_name'], token=HF_TOKEN)
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings

        if not os.path.exists(memory_config['save_dir']):
            os.mkdir(memory_config['save_dir'])

        self.method: LightRAG = LightRAG(
            working_dir=memory_config['save_dir'],
            embedding_func=EmbeddingFunc(
                embedding_dim=memory_config['embedding_dim'],
                max_token_size=memory_config['embedding_max_token_size'],
                func=embedding_func,
            ),
            llm_model_func=ollama_complete_func,
            llm_model_kwargs={"base_url": memory_config['llm_base_url'], "max_completion_tokens": 32768, 'timeout': 60},
            llm_model_name=memory_config['llm_model_name']
        )
        asyncio.run(self.method.initialize_storages())

        self.config = memory_config
        self.qa_config = qa_config
        self.method_params = QueryParam(mode="hybrid")

    @staticmethod
    def prepare_qaeval_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        return list()

    @staticmethod
    def prepare_qa_config() -> Dict:
        return dict()

    def perform_qa(self, questions: List[str]) -> List[str]:
        answers = []
        for question in questions:
            answer = asyncio.run(self.method.aquery(question,param=self.method_params))
            answers.append(answer)

        return answers

if __name__ == "__main__":

    kgconnparams_path = "./debug/example/kgconn_params.yaml"  # TO CHANGE
    with open(kgconnparams_path, 'r') as stream:
        example_kgconn_params = yaml.safe_load(stream)

    envparams_path = "./debug/example/qaenv_params.yaml" # TO CHANGE
    with open(envparams_path, 'r') as stream:
        example_env_params = yaml.safe_load(stream)

    memoryconfig_path = "./debug/example/kg_config"  # TO CHANGE
    with open(memoryconfig_path, 'r', encoding='utf-8') as fd:
        example_memory_config = json.loads(fd.read())

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
    env_params = Hipporag2QAOperations.prepare_qaeval_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated qa config:")
    qa_config = Hipporag2QAOperations.prepare_qa_config()
    print(qa_config)

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
    queries = [
        "What is George Rankin's occupation?",
        "How did Cinderella reach her happy ending?",
        "What county is Erik Hort's birthplace a part of?"
    ]
    real_answers = [
        ["Politician"],
        ["By going to the ball."],
        ["Rockland County"]
    ]

    print("Initializing method...")
    method = Hipporag2QAOperations(example_memory_config, qa_config)
    # method.build_graph(example_documents)
    # print("Builded graph info:")
    # method.print_graph_info()

    print("Performing QA...")
    for query, real_answer in zip(queries, real_answers):
        predicted_answer = method.perform_qa([query])[0]
        print(f"query: {query}; real_answer: {real_answer}; predicted_answer: {predicted_answer}")

    print("Done!")
