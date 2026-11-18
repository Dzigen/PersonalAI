from .configs import EVAL_JUDGE_MAIN_LOG_PATH
from .utils import LLMasaJudgeAgentTasksConfig
from ..utils import AgentDriver, AgentDriverConfig, \
    Logger, ReturnStatus, ReturnInfo, \
        AgentTaskSolver, CacheUtils
from ..utils.data_structs import LoggingConfig, BaseConfigOperations
from ..utils.EnvironmentConnectionUtils import EnvironmentConnectionUtils
from dataclasses import dataclass, field
from typing import Union, Dict, List
from copy import deepcopy

@dataclass
class AnswersJudgeConfig(BaseConfigOperations, LoggingConfig):
    lang: str = 'auto'
    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    agent_tasks_config: Union[LLMasaJudgeAgentTasksConfig, Dict] = field(default_factory=lambda: LLMasaJudgeAgentTasksConfig())
    cache_table_name: Union[str, None] = 'qaeval_judge_cache'

    verbose: bool = False
    cache_table_name: str = "qaeval_judge_cache"
    log_relative_path: str = EVAL_JUDGE_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.adriver_config.to_str()}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswersJudgeConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.adriver_config, dict):
            self.adriver_config = AgentDriverConfig.from_dict(self.adriver_config)
        else:
            self.adriver_config.formate_fields()

        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = LLMasaJudgeAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()



class AnswersJudge(CacheUtils, EnvironmentConnectionUtils):

    def __init__(self, config: AnswersJudgeConfig = AnswersJudgeConfig(),
                 cache_kvdriver_config: object = None,
                 cache_llm_inference: bool = False):
        if isinstance(config, dict):
            config: AnswersJudgeConfig = AnswersJudgeConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs(self.config.verbose, self.config.log_level, self.config.log_base_path)

        self.config = config

        self.cachekv = self.init_cachekv(cache_kvdriver_config, self.config.cache_table_name)
        self.agent = AgentDriver.select(config.adriver_config)

        llmjudge_task_cache_config = None
        if cache_llm_inference:
            llmjudge_task_cache_config = deepcopy(cache_kvdriver_config)

        self.llmjudge_solver = AgentTaskSolver(
            self.agent, self.config.agent_tasks_config.llmasajudge,
            llmjudge_task_cache_config)

        self.log = Logger(self.config.log_relative_path, self.config.log_base_path)
        self.verbose = config.verbose
        self.log_level = config.log_level

    def open_connections(self):
        self.agent.open_connection()
        self.llmjudge_solver.open_connections()

    def close_connections(self):
        self.agent.close_connection()
        self.llmjudge_solver.close_connections()

    def get_cache_key(self, question: str, ground_truth: str, predicted_response: Union[str, None]) -> List[str]:
        return [question, ground_truth, str(predicted_response), self.config.to_str()]

    @CacheUtils.cache_method_output
    def perform(self, question: str, ground_truth: str, predicted_response: str) -> Union[int, float]:
        info = ReturnInfo()
        self.log.info("START JUDGING...", verbose=self.verbose, log_level=self.log_level)
        self.log.info(f"* QUESTION: {question}",verbose=self.verbose)
        self.log.info(f"* GROUND_TRUTH: {ground_truth}", verbose=self.verbose, log_level=self.log_level)
        self.log.info(f"* PREDICTED: {predicted_response}", verbose=self.verbose, log_level=self.log_level)

        predicted_score, status, _ = self.llmjudge_solver.solve(
            lang=self.config.lang, question=question,
            gold_answer=ground_truth, generated_answer=predicted_response)

        if status != ReturnStatus.success:
            info.occurred_warning.append(status)
        self.log.info(f"RESULT: {predicted_score}", verbose=self.verbose, log_level=self.log_level)

        return predicted_score, info
