from .configs import DEFAULT_LLMJUDGE_TASK_CONFIG, EVAL_JUDGE_MAIN_LOG_PATH
from dataclasses import dataclass, field
from typing import Union
from copy import deepcopy
import sys

BASE_PATH = '../../'
sys.path.insert(0, BASE_PATH)

from src.db_drivers.kv_driver import KeyValueDriverConfig
from src.utils.cache_kv import CacheKV, CacheUtils
from src.agents import AgentDriver, AgentDriverConfig
from src.utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from src.utils.logger import LogLevel

@dataclass
class AnswersJudgeConfig:
    lang: str = 'auto'
    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    llmjudge_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_LLMJUDGE_TASK_CONFIG)
    cache_table_name: Union[str, None] = 'qaeval_judge_cache'

    log_path: Logger = EVAL_JUDGE_MAIN_LOG_PATH
    verbose: bool = False
    log_level: LogLevel = LogLevel.DEBUG

    cache_table_name: str = "qaeval_judge_cache"


class AnswersJudge(CacheUtils):

    def __init__(self, config: AnswersJudgeConfig = AnswersJudgeConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None,
                 cache_llm_inference: bool = False):

        self.log = Logger(config.log_path)
        self.verbose = config.verbose
        self.log_level = config.log_level
        self.config = config

        self.cachekv = self.init_cachekv(cache_kvdriver_config, self.config.cache_table_name)
        self.agent = AgentDriver.connect(config.adriver_config)

        llmjudge_task_cache_config = None
        if cache_llm_inference:
            llmjudge_task_cache_config = deepcopy(cache_kvdriver_config)

        self.llmjudge_solver = AgentTaskSolver(
            self.agent, self.config.llmjudge_task_config,
            llmjudge_task_cache_config)

    def get_cache_key(self, question: str, ground_truth: str, predicted_response: Union[str, None]):
        return [question, ground_truth, str(predicted_response), self.config.adriver_config.to_str(),
                self.config.llmjudge_task_config.version]

    @CacheUtils.cache_method_output
    def perform(self, question: str, ground_truth: str, predicted_response: str) -> Union[int, float]:
        info = ReturnInfo()
        self.log.info("START JUDGING...", 
                      verbose=self.verbose, log_level=self.log_level)
        self.log.info(f"* GROUND_TRUTH: {ground_truth}",
                 verbose=self.verbose, log_level=self.log_level)
        self.log.info(f"* PREDICTED: {predicted_response}",
                 verbose=self.verbose, log_level=self.log_level)

        predicted_score, status, _ = self.llmjudge_solver.solve(
            lang=self.config.lang, question=question,
            gold_answer=ground_truth, generated_answer=predicted_response)

        if status != ReturnStatus.success:
            info.occurred_warning.append(status)
        self.log.info(f"RESULT: {predicted_score}", 
                      verbose=self.verbose, log_level=self.log_level)

        return predicted_score, info
