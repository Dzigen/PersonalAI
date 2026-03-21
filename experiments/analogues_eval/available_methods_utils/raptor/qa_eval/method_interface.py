import sys
import yaml
from typing import List, Dict
import json

EXPEROMETS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPEROMETS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGQAOperations
from analogues_eval.available_methods_utils.raptor.kg_building import RaptorBuildOperations

class RaptorQAOperations(GraphRAGQAOperations, RaptorBuildOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict) -> None:
        # костыль
        RAPTOR_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/raptor/method_source" # TO CHANGE
        sys.path.insert(0, RAPTOR_SOURCE_PATH)
        from raptor import RetrievalAugmentation, RetrievalAugmentationConfig, SBertEmbeddingModel
        
        UTILS_SOURCE_PATH="/home/workspace/experiments/analogues_eval/available_methods_utils/raptor"  # TO CHANGE
        sys.path.insert(0, UTILS_SOURCE_PATH)
        from utils import CustomQAModel, CustomSummarizationModel

        formated_config = RetrievalAugmentationConfig(
            summarization_model=CustomSummarizationModel(
                model_name=memory_config['llm_model_name'], base_url=memory_config['llm_base_url']
            ),
            qa_model=CustomQAModel(
                model_name=memory_config['llm_model_name'], base_url=memory_config['llm_base_url']
            ),
            embedding_model=SBertEmbeddingModel(
                model_name=memory_config['embedding_model_name']
            )
        )
        self.method = RetrievalAugmentation(config=formated_config, tree=f"{memory_config['save_dir']}/storage")
        self.config = memory_config
        self.qa_config = qa_config

    @staticmethod
    def prepare_qaeval_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        return list()

    @staticmethod
    def prepare_qa_config() -> Dict:
        return dict()

    def perform_qa(self, questions: List[str]) -> List[str]:
        answers = []
        for question in questions:
            answer = self.method.answer_question(question=question)
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
    env_params = RaptorQAOperations.prepare_qaeval_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated qa config:")
    qa_config = RaptorQAOperations.prepare_qa_config()
    print(qa_config)

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
    method = RaptorQAOperations(example_memory_config, qa_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing QA...")
    for query, real_answer in zip(queries, real_answers):
        predicted_answer = method.perform_qa([query])[0]
        print(f"query: {query}; real_answer: {real_answer}; predicted_answer: {predicted_answer}")

    print("Done!")
