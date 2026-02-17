from kg_gen import KGGen, Graph
import yaml
from typing import List, Dict
from ...utils import GraphRAGQAOperations

class KGGenQAOperations(GraphRAGQAOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict) -> None:
        self.method: KGGen = KGGen(
            model=memory_config['llm_model_name'],
            temperature=memory_config['temperature'],
            reasoning_effort=memory_config['reasoning_effort'],
            max_tokens=memory_config['max_tokens'],
            api_base=memory_config['llm_base_url'],
            retrieval_model=memory_config['embedding_model_name']
        )
        self.memory_config: Dict = memory_config
        self.qa_config = qa_config
        self.aggregated_graph: Graph = self.method.from_file(f"{memory_config['save_dir']}/graph.json")

    @staticmethod
    def prepare_qaeval_env_params(self, conn_params: Dict, env_params: Dict) -> List[Dict[str,str]]:
        return list()

    @staticmethod
    def prepare_qa_config(self) -> Dict:
        raise NotImplementedError

    def perform_qa(self, questions: List[str]) -> List[str]:
        raise NotImplementedError

if __name__ == "__main__":

    envparams_path = "./debug/example/qaenv_params.yaml" # TO CHANGE
    with open(envparams_path, 'r') as stream:
        example_env_params = yaml.safe_load(stream)

    kgconnparams_path = "./debug/example/kgconn_params.yaml"  # TO CHANGE
    with open(kgconnparams_path, 'r') as stream:
        example_kgconn_params = yaml.safe_load(stream)

    memoryconfig_path = "./debug/example/kg_config.yaml"  # TO CHANGE
    with open(memoryconfig_path, 'r') as stream:
        example_memory_config = yaml.safe_load(stream)

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
    env_params = KGGenQAOperations.prepare_qaeval_env_params(
        example_kgconn_params, example_env_params)
    print(env_params)

    print("Generated qa config:")
    qa_config = KGGenQAOperations.prepare_qa_config()
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
    method = KGGenQAOperations(example_memory_config, qa_config)
    print("Builded graph info:")
    method.print_graph_info()

    print("Performing QA...")
    for query, real_answer in zip(queries, real_answers):
        predicted_answer = method.perform_qa([query])[0]
        print(f"query: {query}; real_answer: {real_answer}; predicted_answer: {predicted_answer}")

    print("Done!")
