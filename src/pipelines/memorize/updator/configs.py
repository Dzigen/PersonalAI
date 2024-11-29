from ....utils import AgentTaskSolverConfig, AgentTaskSuite, Logger

from ....prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT

from ....parsers.memorize_pipeline.updator.replace_simple_triplets import rs_custom_parse, rs_custom_postprocess, rs_custom_formate
from ....prompts.memorize_pipeline.updator.replace_simple_triplets import RU_REPLACE_SIMPLE_USER_PROMPT, EN_REPLACE_SIMPLE_USER_PROMPT

from ....parsers.memorize_pipeline.updator.replace_thesis_triplets import rt_custom_parse, rt_custom_postprocess, rt_custom_formate
from ....prompts.memorize_pipeline.updator.replace_thesis_triplets import RU_REPLACE_THESIS_USER_PROMPT, EN_REPLACE_THESIS_USER_PROMPT

MEM_UPDATOR_MAIN_LOG_PATH = "log/memorize/updator/main"
MEM_REPLACE_SIMPLE_LOG_PATH = 'log/memorize/updator/replace_simple_triplets'
MEM_REPLACE_THESIS_LOG_PATH = 'log/memorize/updator/replace_thesis_triplets'

### AGENT TASK-SUITES ###

# REPLACE SIMPLE TRIPLETS

EN_REPLACE_SIMPLE_SUITE = AgentTaskSuite(
    system_prompt=EN_SYSTEM_PROMPT,
    user_prompt=EN_REPLACE_SIMPLE_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rs_custom_parse,
    postprocess_answer_func=rs_custom_postprocess
)

RU_REPLACE_SIMPLE_SUITE = AgentTaskSuite(
    system_prompt=RU_SYSTEM_PROMPT,
    user_prompt=RU_REPLACE_SIMPLE_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rs_custom_parse,
    postprocess_answer_func=rs_custom_postprocess
)

DEFAULT_REPLACE_SIMPLE_SUITES = {'ru': RU_REPLACE_SIMPLE_SUITE, 'en': EN_REPLACE_SIMPLE_SUITE}

DEFAULT_REPLACE_SIMPLE_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_REPLACE_SIMPLE_SUITES,
    formate_context_func=rs_custom_formate,
    log=Logger(MEM_REPLACE_SIMPLE_LOG_PATH)
)

# REPLACE THESIS TRIPLETS

EN_REPLACE_THESIS_SUITE = AgentTaskSuite(
    system_prompt=EN_SYSTEM_PROMPT,
    user_prompt=EN_REPLACE_THESIS_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rt_custom_parse,
    postprocess_answer_func=rt_custom_postprocess
)

RU_REPLACE_THESIS_SUITE = AgentTaskSuite(
    system_prompt=RU_SYSTEM_PROMPT,
    user_prompt=RU_REPLACE_THESIS_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rt_custom_parse,
    postprocess_answer_func=rt_custom_postprocess
)

DEFAULT_REPLACE_THESIS_SUITES = {'ru': RU_REPLACE_THESIS_SUITE, 'en': EN_REPLACE_THESIS_SUITE}

DEFAULT_REPLACE_THESIS_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_REPLACE_THESIS_SUITES,
    formate_context_func=rt_custom_formate,
    log=Logger(MEM_REPLACE_THESIS_LOG_PATH)
)
