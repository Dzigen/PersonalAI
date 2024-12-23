import pytest

import sys
sys.path.insert(0, "../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

from cases import INIT_EPISODIC_KNOWLEDGE_GRAPH

@pytest.mark.parametrize("kg_triplets, triplets, agent_stub_answers, expected_obsolete_ids", [
    # 1. не найдено устаревших трипелтов
    # 1.1. нуль сопоставленных вершин
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 1.2. нуль смежных вершин
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 1.3. нуль ids от agent-солвера
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 2. найден один устаревший триплет
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 3. найдено несколько устаревших триплетов (разные замены)
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 4. найдено несколько устаревших триплетов (итеративная замена того же ребра)
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], []),
    # 5. ошибка при разборе сгенерированного ответа (parser error)
    (INIT_EPISODIC_KNOWLEDGE_GRAPH, [], [], [])
])
def test_find_episodic(llm_updator: LLMUpdator, kg_triplets: List[Triplet], triplets: List[Triplet],
                     agent_stub_answers: List[str], expected_obsolete_ids: List[str]):
    llm_updator.kg_model.clear()
    llm_updator.kg_model.add_knowledge(kg_triplets)

    for triplet, stub_answer, expected_output in zip(triplets, agent_stub_answers, expected_obsolete_ids):

        llm_updator.agent.looped_answers.clear()
        llm_updator.agent.looped_answers += stub_answer

        real_obsolete_ids  = llm_updator.find_hyper_obsolete_triplet_ids([triplet])

        assert expected_output == real_obsolete_ids

        if len(real_obsolete_ids) > 0:
            obsolete_triplets = llm_updator.kg_model.graph_struct.db_conn.read(real_obsolete_ids)

            llm_updator.kg_model.remove_knowledge(obsolete_triplets)
            llm_updator.kg_model.add_knowledge([triplet])
