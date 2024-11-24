from ....utils import AgentTaskSolverConfig, AgentTaskSuite, Logger

from ....parsers.memorize_pipeline.extractor.triplet_extraction import etriplets_custom_parse, etriplets_custom_formate, etriplets_custom_postprocess
from ....prompts.memorize_pipeline.extractor.triplet_extraction import EN_TRIPLETS_EXTRACTION_SYSTEM_PROMPT, EN_TRIPLETS_EXTRACTION_USER_PROMPT,\
      RU_TRIPLETS_EXTRACTION_SYSTEM_PROMPT, RU_TRIPLETS_EXTRACTION_USER_PROMPT

from ....parsers.memorize_pipeline.extractor.thesis_extraction import ethesises_custom_parse, ethesises_custom_formate, ethesises_custom_postprocess
from ....prompts.memorize_pipeline.extractor.thesis_extraction import EN_THESISES_EXTRACTION_SYSTEM_PROMPT, EN_THESISES_EXTRACTION_USER_PROMPT,\
      RU_THESISES_EXTRACTION_SYSTEM_PROMPT, RU_THESISES_EXTRACTION_USER_PROMPT

MEM_EXTRACTOR_LOG = "log/memorize/extractor/main"
MEM_EXTRACT_TRIPLETS_LOG = "log/memorize/extractor/extract_triplets"
MEM_EXTRACT_THESISES_LOG = "log/memorize/extractor/extract_thesises"

### AGENT TASK-SUITES ###

# EXTRACT TRIPLETS

EN_EXTRACT_TRIPLETS_SUITE = AgentTaskSuite(
    system_prompt=EN_TRIPLETS_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_TRIPLETS_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=etriplets_custom_parse,
    postprocess_answer_func=etriplets_custom_postprocess
)

RU_EXTRACT_TRIPLETS_SUITE = AgentTaskSuite(
    system_prompt=RU_TRIPLETS_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_TRIPLETS_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=etriplets_custom_parse,
    postprocess_answer_func=etriplets_custom_postprocess
)

DEFAULT_EXTRACT_TRIPLETS_SUITES = {'ru': RU_EXTRACT_TRIPLETS_SUITE, 'en': EN_EXTRACT_TRIPLETS_SUITE}

DEFAULT_EXTRACT_TRIPLETS_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_EXTRACT_TRIPLETS_SUITES,
    formate_context_func=etriplets_custom_formate,
    log=Logger(MEM_EXTRACT_TRIPLETS_LOG)
)

# EXTRACT THESISES

EN_EXTRACT_THESISES_SUITE = AgentTaskSuite(
    system_prompt=EN_THESISES_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_THESISES_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=ethesises_custom_parse,
    postprocess_answer_func=ethesises_custom_postprocess
)

RU_EXTRACT_THESISES_SUITE = AgentTaskSuite(
    system_prompt=RU_THESISES_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_THESISES_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=ethesises_custom_parse,
    postprocess_answer_func=ethesises_custom_postprocess
)

DEFAULT_EXTRACT_THESISES_SUITES = {'ru': RU_EXTRACT_THESISES_SUITE, 'en': EN_EXTRACT_THESISES_SUITE}

DEFAULT_EXTRACT_THESISES_TASK_CONFIG = AgentTaskSolverConfig(
    suites=DEFAULT_EXTRACT_THESISES_SUITES,
    formate_context_func=ethesises_custom_formate,
    log=Logger(MEM_EXTRACT_THESISES_LOG)
)
