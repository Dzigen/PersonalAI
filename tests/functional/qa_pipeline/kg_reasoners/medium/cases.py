import sys
from copy import deepcopy
from functools import reduce
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.kg_reasoning.medium_reasoner import MediumKGReasonerConfig
from src.pipelines.qa.knowledge_retriever import KnowledgeRetrieverConfig

from ...cases import QUESTIONS
from ..knowledge_retriever.cases import KG_TRAVERSE_METHODS, FILTER_METHODS

LANGUAGES = ['en', 'ru']
GENERATE_SOMETHING = [True, False]

POPULATED_MEDIUM_REASONER_TEST_CASES = []
for retrieval_config in KG_TRAVERSE_METHODS:
    for filter_method_config in FILTER_METHODS:
        for language in LANGUAGES:
            for query in QUESTIONS[language]:
                for flag in GENERATE_SOMETHING:
                    t_name, t_config = retrieval_config[0], deepcopy(retrieval_config[1])
                    f_name, f_config = filter_method_config[0], deepcopy(filter_method_config[1])

                    reasoner_config = MediumKGReasonerConfig(
                        knowledge_retriever_config=KnowledgeRetrieverConfig(
                            retriever_method=t_name,
                            retriever_config=t_config,
                            filter_method=f_name,
                            filter_config=f_config
                        ),
                        answer_something=flag
                    )

                    POPULATED_MEDIUM_REASONER_TEST_CASES.append([reasoner_config, query, language])
