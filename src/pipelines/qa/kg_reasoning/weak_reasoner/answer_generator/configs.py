from ......utils import AgentTaskSuite, AgentTaskSolverConfig, Logger

from ......parsers.qa_pipeline.answer_generator.question_answering import ag_custom_formate, ag_custom_postprocess,\
      ru_ag_custom_answer_parse, en_ag_custom_answer_parse

from ......prompts.qa_pipeline.answer_generator.question_answering import RU_AG_USER_PROMPT, EN_AG_USER_PROMPT
from ......prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT

ANSWER_GENERATION_LOG_PATH = 'log/qa/kg_reasoner/weak/answer_generation'

EN_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=EN_SYSTEM_PROMPT,
    user_prompt=EN_AG_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=en_ag_custom_answer_parse,
    postprocess_answer_func=ag_custom_postprocess
)

RU_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=RU_SYSTEM_PROMPT,
    user_prompt=RU_AG_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=ru_ag_custom_answer_parse,
    postprocess_answer_func=ag_custom_postprocess
)

DEFAULT_ANSWER_GEN_SUITE = {'ru': RU_ANSWER_GEN_SUITE, 'en': EN_ANSWER_GEN_SUITE}

DEFAULT_ANSWER_GEN_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_ANSWER_GEN_SUITE,
    formate_context_func=ag_custom_formate,
    log=Logger(ANSWER_GENERATION_LOG_PATH)
)
