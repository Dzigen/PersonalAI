import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet, ReturnStatus
from src.utils import AgentTaskSolver
from typing import List

@pytest.mark.parametrize("lang, base_triplet, incident_triplets, agent_stub_answers, expected_thesis_ids, expected_status", [
    # 1. русский язык
    # 1.1. позитивный тест
    # 1.1.1 найдена одна устаревшая связь
    ('ru', ..., ..., ..., ..., ..., ReturnStatus.success),
    # 1.1.2 найдена несколько устаревших связей
    ('ru', ..., ..., ..., ..., ..., ReturnStatus.success),
    # 1.1.3 устаревший связей не найдено
    ('ru', ..., ..., ..., ..., ..., ReturnStatus.success),
    # 1.2. ошибка в formater-функции
    ('ru', ..., ..., ..., ..., ..., ReturnStatus.bad_formater),
    # 1.3. ошибка мапинга значений в user-prompt
    # TODO
    # 1.4. ошибка генерации
    # TODO
    # 1.5. ошибка в parser-функции
    ('ru', ..., ..., ..., ..., ..., ReturnStatus.bad_parser),
    # 1.6. ошибка в postprocessor-функции
    # TODO
    # 2. английский язык
    # 2.1. позитивный тест
    ('en', ..., ..., ..., ..., ..., ReturnStatus.success),
    # 2.2. ошибка в formater-функции
    ('en', ..., ..., ..., ..., ..., ReturnStatus.bad_formater),
    # 2.3. ошибка мапинга значений в user-prompt
    # TODO
    # 2.4. ошибка генерации
    # TODO
    # 2.5. ошибка в parser-функции
    ('en', ..., ..., ..., ..., ..., ReturnStatus.bad_parser),
    # 2.6. ошибка в postprocessor-функции
    # TODO
    # 3. ошибка при распознавании языка
    # TODO
])
def test_replace_thesis(replace_thesis_solver: AgentTaskSolver, lang: str, base_triplet: Triplet, incident_triplets: List[Triplet],
                        agent_stub_answers: List[str], expected_thesis_ids: List[str], expected_status: ReturnStatus):
    replace_thesis_solver.agent.looped_answers.clear()
    replace_thesis_solver.agent.looped_answers += agent_stub_answers

    real_thesis_ids, real_status = replace_thesis_solver.solve(
        lang=lang, base_triplet=base_triplet, incident_triplets=incident_triplets)
    assert expected_thesis_ids == real_thesis_ids
    assert expected_status == real_status
