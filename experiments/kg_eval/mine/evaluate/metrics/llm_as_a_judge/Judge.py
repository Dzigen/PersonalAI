from .configs import EVAL_JUDGE_MAIN_LOG_PATH, DEFAULT_LLM_GENSTRATEGY, ResponseEvaluator

import sys
BASE_PATH = '../../'
sys.path.insert(0, BASE_PATH)

from src.utils import Logger
from dataclasses import dataclass, field
import dspy
from typing import Union, Dict

@dataclass
class JudgeConfig:
    model: str = 'qwen2.5:7b'
    host: str = 'localhost'
    port: int = 11437
    gen_strategy: Dict[str, Union[str,int]] = field(default_factory=lambda: DEFAULT_LLM_GENSTRATEGY)
    log: Logger = field(default_factory=lambda: Logger(EVAL_JUDGE_MAIN_LOG_PATH))
    verbose: bool = False

class Judge():

    def __init__(self, config: JudgeConfig = JudgeConfig()):
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
        self.log("START JUDGING...", verbose=self.verbose)
        self.log(f"* QUERY: {query}", verbose=self.verbose)
        self.log(f"* RETRIEVED_CONTEXT: {retrieved_context}",verbose=self.verbose)

        result = self.evaluator.forward(context=retrieved_context, correct_answer=query)
        self.log(f"RESULT: {result.evaluation}", verbose=self.verbose)

        return result.evaluation
