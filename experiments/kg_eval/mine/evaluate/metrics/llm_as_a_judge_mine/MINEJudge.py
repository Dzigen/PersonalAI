from .configs import EVAL_MINEJUDGE_MAIN_LOG_PATH, DEFAULT_LLM_GENSTRATEGY, ResponseEvaluator

import sys
BASE_PATH = '/home/workspace' # TO CHANGE
sys.path.insert(0, BASE_PATH)

from src.utils import Logger
from dataclasses import dataclass, field
import dspy
from typing import Union, Dict

@dataclass
class MINEJudgeConfig:
    model: str = 'qwen2.5:7b'
    host: str = 'localhost'
    port: int = 11437
    gen_strategy: Dict[str, Union[str,int]] = field(default_factory=lambda: DEFAULT_LLM_GENSTRATEGY)
    log: Logger = field(default_factory=lambda: Logger(EVAL_MINEJUDGE_MAIN_LOG_PATH))
    verbose: bool = False

class MINEJudge():

    def __init__(self, config: MINEJudgeConfig = MINEJudgeConfig()):
        self.log = config.log
        self.verbose = config.verbose
        self.config = config

        llm = dspy.LM(
            model=f"ollama_chat/{config.model}",
            api_base=f'http://{config.host}:{config.port}',
            **config.gen_strategy
        )
        dspy.configure(lm=llm)
        self.evaluator = ResponseEvaluator()

    def perform(self, query: str, retrieved_context: str) -> int:
        self.log.debug("START JUDGING...", verbose=self.verbose)
        self.log.debug(f"* QUERY: {query}", verbose=self.verbose)
        self.log.debug(f"* RETRIEVED_CONTEXT: {retrieved_context}",verbose=self.verbose)

        result = self.evaluator(context=retrieved_context, correct_answer=query)
        self.log.debug(f"RESULT: {result.evaluation}", verbose=self.verbose)

        return result.evaluation
