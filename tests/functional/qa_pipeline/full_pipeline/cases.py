import pytest
import sys
from copy import deepcopy
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa import QAPipelineConfig
from src.pipelines.qa.kg_reasoning import KnowledgeGraphReasonerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner import MediumKGReasonerConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig

from ..cases import QUESTIONS


LANGUAGES = ['en', 'ru']

POPULATED_QAPIPELINE_TEST_CASES = []

for language in LANGUAGES:
    for question in QUESTIONS[language]:
        weak_config = QAPipelineConfig(
            lang=language,
            reasoner_config=KnowledgeGraphReasonerConfig(
                reasoner_name='weak',
                reasoner_config=WeakKGReasonerConfig()
            ),
            log_base_path=TEST_VOLUME_DIR
        )
        weak_config.synchronize_language()
        weak_config.synchronize_logging()

        medium_config = QAPipelineConfig(
            lang=language,
            reasoner_config=KnowledgeGraphReasonerConfig(
                reasoner_name='medium',
                reasoner_config=MediumKGReasonerConfig()
            ),
            log_base_path=TEST_VOLUME_DIR
        )
        medium_config.synchronize_language()
        medium_config.synchronize_logging()

        POPULATED_QAPIPELINE_TEST_CASES.append([weak_config, question, language])
        POPULATED_QAPIPELINE_TEST_CASES.append([medium_config, question, language])
