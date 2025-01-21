from ......utils import AgentTaskSuite, AgentTaskSolverConfig, Logger

from ......prompts.qa_pipeline.query_parser.kw_extraction import EN_KW_EXTRACTION_USER_PROMPT, RU_KW_EXTRACTION_USER_PROMPT
from ......prompts.system import EN_SYSTEM_PROMPT, RU_SYSTEM_PROMPT

from ......parsers.qa_pipeline.query_parser.kw_extraction import kwe_custom_formate, kwe_custom_parse, kwe_custom_postprocess

QP_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/main'
KW_EXTRACTION_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/kw_extraction'

EN_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=EN_SYSTEM_PROMPT,
    user_prompt=EN_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=kwe_custom_parse,
    postprocess_answer_func=kwe_custom_postprocess
)

RU_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=RU_SYSTEM_PROMPT,
    user_prompt=RU_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=kwe_custom_parse,
    postprocess_answer_func=kwe_custom_postprocess
)

DEFAULT_KW_EXTRACTION_SUITE = {'ru': RU_KW_EXTRACTION_SUITE, 'en': EN_KW_EXTRACTION_SUITE}

DEFAULT_KW_EXTRACTION_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_KW_EXTRACTION_SUITE,
    formate_context_func=kwe_custom_formate,
    log=Logger(KW_EXTRACTION_LOG_PATH)
)
