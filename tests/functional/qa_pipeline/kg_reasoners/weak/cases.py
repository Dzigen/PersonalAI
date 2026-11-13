import sys
from copy import deepcopy
from functools import reduce
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig
from src.pipelines.qa.knowledge_retriever import KnowledgeRetrieverConfig
from src.pipelines.qa.knowledge_retriever.traversal_methods import NaiveGraphSearchConfig

from ...cases import QUESTIONS
from ..knowledge_retriever.cases import KG_TRAVERSE_METHODS, FILTER_METHODS

LANGUAGES = ['en', 'ru']
POPULATED_WEAK_REASONER_TEST_CASES = []

#
WEAK_REASONER_W_NAIVERETRIEVER_CONFIG = WeakKGReasonerConfig(
    query_parser_config=None,
    knowledge_comparator_config=None,
    knowledge_retriever_config=KnowledgeRetrieverConfig(
        retriever_method='naive_retriever',
        retriever_config=NaiveGraphSearchConfig()
    ),
    log_base_path=TEST_VOLUME_DIR
)
WEAK_REASONER_W_NAIVERETRIEVER_CONFIG.synchronize_logging()
for language in LANGUAGES:
       config = deepcopy(WEAK_REASONER_W_NAIVERETRIEVER_CONFIG)
       config.lang = language
       config.synchronize_language()
       for query in QUESTIONS[language]:
            POPULATED_WEAK_REASONER_TEST_CASES.append([config, query, language])

#
for retrieval_config in KG_TRAVERSE_METHODS:
    for filter_method_config in FILTER_METHODS:
        for language in LANGUAGES:
            for query in QUESTIONS[language]:
                t_name, t_config = retrieval_config[0], deepcopy(retrieval_config[1])
                f_name, f_config = filter_method_config[0], deepcopy(filter_method_config[1])

                reasoner_config = WeakKGReasonerConfig(
                    lang=language,
                    knowledge_retriever_config=KnowledgeRetrieverConfig(
                        retriever_method=t_name,
                        retriever_config=t_config,
                        filter_method=f_name,
                        filter_config=f_config
                    ),
                    log_base_path=TEST_VOLUME_DIR
                )
                reasoner_config.synchronize_language()
                reasoner_config.synchronize_logging()

                POPULATED_WEAK_REASONER_TEST_CASES.append([reasoner_config, query, language])
