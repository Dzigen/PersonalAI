import pytest

import sys
sys.path.insert(0, "../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

from cases import INIT_KNOWLEDGE_GRAPH

@pytest.mark.parametrize("kg_triplets, triplets, agent_stub_answers, expected_obsolete_ids", [
    # не найдено устаревших трипелтов
    (INIT_KNOWLEDGE_GRAPH, [], [], []),
    # найден один устаревший триплет
    (INIT_KNOWLEDGE_GRAPH, [], [], []),
    # найдено несколько устаревших триплетов (разные замены)
    (INIT_KNOWLEDGE_GRAPH, [], [], []),
    # найдено несколько устаревших триплетов (одинаковые замены)
    (INIT_KNOWLEDGE_GRAPH, [], [], []),
    # ошибка при разборе сгенерированного ответа (parser error)
    (INIT_KNOWLEDGE_GRAPH, [], [], []),
])
def test_find_simple(llm_updator: LLMUpdator, kg_triplets: List[Triplet], triplets: List[Triplet],
                     agent_stub_answers: List[str], expected_obsolete_ids: List[str]):
    llm_updator.kg_model.clear()
    llm_updator.kg_model.add_knowledge(kg_triplets)

    llm_updator.agent.looped_answers.clear()
    llm_updator.agent.looped_answers += agent_stub_answers

    real_obsolete_ids  = llm_updator.find_simple_obsolete_triplet_ids(triplets)

    assert expected_obsolete_ids == real_obsolete_ids
