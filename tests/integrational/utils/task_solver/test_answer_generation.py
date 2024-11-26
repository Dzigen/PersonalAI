import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import ReturnStatus, Triplet
from src.utils import AgentTaskSolver
from typing import List, Dict

@pytest.mark.parametrize("lang, query, context_triplets, agent_stub_answers, expected_answer, expected_status", [
    # 1. русский язык
    # 1.1. позитивный тест
    ()
    # 1.2. ошибка в formater-функции
    # 1.3. ошибка мапинга значений в user-prompt
    # 1.4. ошибка генерации
    # 1.5. ошибка в parser-функции
    # 1.6. ошибка в postprocessor-функции
    # 2. английский язык
    # 2.1. позитивный тест
    # 2.2. ошибка в formater-функции
    # 2.3. ошибка мапинга значений в user-prompt
    # 2.4. ошибка генерации
    # 2.5. ошибка в parser-функции
    # 2.6. ошибка в postprocessor-функции
    # 3. ошибка при распознавании языка
])
def test_answer_generation(ag_solver: AgentTaskSolver, lang: str, query: str, context_triplets: List[Triplet],
                           agent_stub_answers: List[str], expected_answer: str, expected_status: ReturnStatus):
    ag_solver.agent.looped_answers.clear()
    ag_solver.agent.looped_answers += agent_stub_answers

    real_answer, real_status = ag_solver.solve(lang, query=query, context_tripelets=context_triplets)
    assert expected_answer == real_answer
    assert expected_status == real_status
