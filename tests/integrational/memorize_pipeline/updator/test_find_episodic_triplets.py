import pytest

import sys
sys.path.insert(0, "../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

from cases import INIT_KNOWLEDGE_GRAPH

@pytest.mark.parametrize("kg_triplets, hyper_triplets, episodic_triplets, agent_stub_answers, expected_hyper_obsolete_ids, expected_episodic_obsolete_ids", [
    # 1. не найдено устаревших трипелтов
    # 1.1. нуль сопоставленных вершин
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
    # 1.2. нуль смежных вершин
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
    # 1.3. нуль ids от agent-солвера
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
    # 2. найден один устаревший триплет
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
    # 3. найдено несколько устарев ших триплетов (разные замены)
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
    # 4. найдено несколько устаревших триплетов (итеративная замена того же ребра)
    (INIT_KNOWLEDGE_GRAPH, [], [], [], []),
])
def test_find_episodic(llm_updator: LLMUpdator, kg_triplets: List[Triplet], hyper_triplets: List[Triplet],
                     episodic_triplets: List[Triplet], agent_stub_answers: List[str], expected_hyper_obsolete_ids: List[str],
                     expected_episodic_obsolete_ids: List[str]):
    llm_updator.kg_model.clear()
    llm_updator.kg_model.add_knowledge(kg_triplets)

    for triplet, stub_answer, h_triplets, expected_h_output, expected_output in zip(episodic_triplets, agent_stub_answers, hyper_triplets, expected_hyper_obsolete_ids, expected_episodic_obsolete_ids):

        llm_updator.agent.looped_answers.clear()
        llm_updator.agent.looped_answers += stub_answer

        obsolete_hyper_ids = []
        for h_t in h_triplets:
            obsolete_hyper_ids += llm_updator.find_hyper_obsolete_triplet_ids([h_t])

        assert expected_h_output == obsolete_hyper_ids

        real_obsolete_ids  = llm_updator.find_episodic_obsolete_triplet_ids([triplet], obsolete_hyper_ids)

        assert expected_output == real_obsolete_ids

        if len(real_obsolete_ids) > 0:
            obsolete_triplets = llm_updator.kg_model.graph_struct.db_conn.read(real_obsolete_ids)

            llm_updator.kg_model.remove_knowledge(obsolete_triplets)
            llm_updator.kg_model.add_knowledge([triplet])
