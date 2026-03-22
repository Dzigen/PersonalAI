import yaml
from typing import List, Dict
import json
import sys

EXPERIMENTS_BASE_PATH="/home/workspace/experiments"
sys.path.insert(0, EXPERIMENTS_BASE_PATH)

from analogues_eval.available_methods_utils.utils import GraphRAGQAOperations
from analogues_eval.available_methods_utils.wikontic.utils import CustomWikontic, create_id
from analogues_eval.available_methods_utils.wikontic.kg_building import WikonticBuildOperations

class WikonticQAOperations(GraphRAGQAOperations, WikonticBuildOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict) -> None:
        self.method = CustomWikontic(memory_config)
        self.config = memory_config
        self.qa_config = qa_config

    @staticmethod
    def prepare_qaeval_env_params(conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
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

    @staticmethod
    def prepare_qa_config() -> Dict:
        return dict()

    def perform_qa(self, questions: List[str]) -> List[str]:
        answers = []
        for question in questions:
            ents = self.method.inferer.identify_relevant_entities_from_question_with_llm(question)
            _, answer = self.method.inferer.answer_question_with_llm(question, linked_entities=ents)
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
    env_params = WikonticQAOperations.prepare_qaeval_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated qa config:")
    qa_config = WikonticQAOperations.prepare_qa_config()
    print(qa_config)

    queries = [
        "What is George Rankin's occupation?",
        "How did Cinderella reach her happy ending?",
        "What county is Erik Hort's birthplace a part of?"
    ]
    real_answers = [
        "Politician",
        "By going to the ball.",
        "Rockland County"
    ]

    print("Initializing method...")
    method = WikonticQAOperations(example_memory_config, qa_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing QA...")
    for query, real_answer in zip(queries, real_answers):
        predicted_answer = method.perform_qa([query])[0]
        print(f"query: {query}; real_answer: {real_answer}; predicted_answer: {predicted_answer}")

    print("Done!")
