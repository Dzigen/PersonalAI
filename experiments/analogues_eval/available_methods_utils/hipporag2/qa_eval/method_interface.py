import yaml
from typing import List, Dict
import sys
import json

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGQAOperations
from analogues_eval.available_methods_utils.hipporag2.kg_building import Hipporag2BuildOperations

class Hipporag2QAOperations(GraphRAGQAOperations, Hipporag2BuildOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict) -> None:
        # костыль
        HIPPORAG_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/hipporag2/method_source/src"  # TO CHANGE
        sys.path.insert(0, HIPPORAG_SOURCE_PATH)
        from hipporag import HippoRAG
        
        self.method = HippoRAG(**memory_config)
        self.method.global_config.save_openie = False # костыль
        self.config = memory_config
        self.qa_config = qa_config

    @staticmethod
    def prepare_qaeval_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        return list()

    @staticmethod
    def prepare_qa_config() -> Dict:
        return dict()

    def perform_qa(self, questions: List[str]) -> List[str]:
        rag_results = self.method.rag_qa(queries=questions)
        answers = [qa_result.answer for qa_result in rag_results[0]]
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
