from .configs import EVAL_RAGAS_MAIN_LOG_PATH
from src.db_drivers.kv_driver import KeyValueDriverConfig
from src.utils.cache_kv import CacheKV, CacheUtils
from src.agents import AgentDriverConfig
from src.utils import Logger, ReturnInfo

from openai import AsyncOpenAI
from dataclasses import dataclass, field
from typing import Union
from time import time
from typing import List, Dict, Tuple
import asyncio
from ragas.llms import llm_factory
from ragas.metrics.collections import DistanceMeasure
from ragas.metrics.collections import RougeScore, CHRFScore, BleuScore, \
    NonLLMStringSimilarity, FactualCorrectness, ResponseGroundedness, \
        ContextRelevance, AnswerAccuracy, Faithfulness, \
            NoiseSensitivity, ContextEntityRecall
from copy import deepcopy
import sys


BASE_PATH = '../../'
sys.path.insert(0, BASE_PATH)


@dataclass
class RagasMetricsConfig:
    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    cache_table_name: Union[str, None] = 'qaeval_ragas_cache'

    log: Logger = field(default_factory=lambda: Logger(EVAL_RAGAS_MAIN_LOG_PATH))
    verbose: bool = False

    cache_table_name: str = "qaeval_ragas_cache"


class RagasMetrics(CacheUtils):

    def __init__(self, config: RagasMetricsConfig = RagasMetricsConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None):

        self.log = config.log
        self.verbose = config.verbose
        self.config = config

        if cache_kvdriver_config is not None and self.config.cache_table_name is not None:
            cache_config = deepcopy(cache_kvdriver_config)
            cache_config.db_config.db_info['table'] = self.config.cache_table_name
            self.cachekv = CacheKV(cache_config)
        else:
            self.cachekv = None

        if config.adriver_config.name != 'ollama':
            raise ValueError

        agent_config = config.adriver_config.agent_config
        base_url = f"http://{agent_config.credentials['host']}:{agent_config.credentials['port']}/v1"
        self.client = AsyncOpenAI(api_key='ollama', base_url=base_url,
                             timeout=agent_config.ext_params['timeout'])


        self.agent = llm_factory(agent_config.credentials['model'], client=self.client)

        self.ContextEntitiesRecall = ContextEntityRecall(llm=self.agent)
        self.NoiseSensitivity = NoiseSensitivity(llm=self.agent)
        self.Faithfulness = Faithfulness(llm=self.agent)
        self.AnswerAccuracy = AnswerAccuracy(llm=self.agent)
        self.ContextRelevance = ContextRelevance(llm=self.agent)
        self.ResponseGroundedness = ResponseGroundedness(llm=self.agent)
        self.FactualCorrectness = FactualCorrectness(llm=self.agent)

        self.NonLllmSimilarity = NonLLMStringSimilarity(distance_measure=DistanceMeasure.LEVENSHTEIN)
        self.BleuScore = BleuScore()
        self.RougeScore = RougeScore(rouge_type="rougeL", mode="fmeasure")
        self.CHRFScore = CHRFScore()

        self.AVAILABLE_METRICS_MAP = {
            'response_groundedness': self.response_groundedness,
            'context_relevance': self.context_relevance,
            'faithfulness': self.faithfulness,
            'context_entity_recall': self.context_entity_recall
        }

    async def context_entity_recall(self, reference: str, retrieved_contexts: List[str]) -> float:
        if len(retrieved_contexts) < 1:
            return 0.0

        output = await self.ContextEntitiesRecall.ascore(
            reference=reference, retrieved_contexts=retrieved_contexts
        )
        return round(output.value,5)

    async def noise_sensitivity(self, user_input: str, response: str, reference: str,
                          retrieved_contexts: List[str]) -> float:
        output = await self.NoiseSensitivity.ascore(
            user_input=user_input, response=response,
            reference=reference, retrieved_contexts=retrieved_contexts
        )
        return round(output.value,5)

    async def faithfulness(self, user_input: str, response: str,
                     retrieved_contexts: List[str]) -> float:
        if len(retrieved_contexts) < 1:
            return 0.0

        output = await self.Faithfulness.ascore(
            user_input=user_input, response=response,
            retrieved_contexts=retrieved_contexts
        )
        return round(output.value,5)

    async def answer_accuracy(self, user_input: str, response: str,
                     reference: str) -> float:
        output = await self.AnswerAccuracy.ascore(
            user_input=user_input, response=response,
            reference=reference
        )
        return round(output.value,5)

    async def context_relevance(self, user_input: str, retrieved_contexts: List[str]) -> float:
        output = await self.ContextRelevance.ascore(
            user_input=user_input, retrieved_contexts=retrieved_contexts
        )
        return round(output.value,5)

    async def response_groundedness(self, response: str, retrieved_contexts: List[str]) -> float:
        if len(retrieved_contexts) < 1:
            return 0.0

        output = await self.ResponseGroundedness.ascore(
            response=response, retrieved_contexts=retrieved_contexts
        )
        return round(output.value,5)

    async def factual_correctness(self, response: str, reference: str) -> float:
        output = await self.FactualCorrectness.ascore(
            response=response, reference=reference
        )
        return round(output.value,5)

    async def nonllm_scores(self, response: str, reference: str) -> Dict[str, float]:
        nonllmsim_output = await self.NonLllmSimilarity.ascore(
            reference=reference, response=response)
        bleu_output = await self.BleuScore.ascore(
            reference=reference, response=response)
        rouge_output = await self.RougeScore.ascore(
            reference=reference, response=response)
        chrf_output = await self.CHRFScore.ascore(
            reference=reference, response=response)

        return {
            'Levenshtein': round(nonllmsim_output.value,5), 'bleu': round(bleu_output.value,5),
            'rougel': round(rouge_output.value,5),'chrf': round(chrf_output.value,5)
        }

    def get_cache_key(self, metric_name, **kwargs):
        user_input = kwargs.get('user_input', None)
        reference = kwargs.get('reference', None)

        response = kwargs.get('response', None)
        retrieved_contexts = kwargs.get('retrieved_contexts', None)
        if retrieved_contexts is not None:
            retrieved_contexts = ';'.join(sorted(retrieved_contexts, reverse=False))

        return [metric_name, user_input, response, reference, retrieved_contexts, self.config.adriver_config.to_str()]

    def get_cached_score(self, metric_name, **kwargs) -> Tuple[bool, Union[None, float]]:
        cache_hit, output = True, None

        cache_key = self.get_cache_key(metric_name, **kwargs)
        cstatus, _, cached_result = self.cachekv.load_value(key=cache_key)
        if cstatus == 0:
            self.log.debug("Cache Hit!", verbose=self.verbose)
            output = cached_result
            self.log.debug(f"* METRIC_NAME: {metric_name}", verbose=self.verbose)
            self.log.debug(f"* USER_INPUT: {kwargs.get('user_input', None)}", verbose=self.verbose)
            self.log.debug(f"* REFERENCE: {kwargs.get('reference', None)}", verbose=self.verbose)
            self.log.debug(f"* RESPONSE: {kwargs.get('response', None)}",verbose=self.verbose)
            self.log.debug(f"* RETRIEVED_CONTEXTS: {kwargs.get('retrieved_contexts', None)}",verbose=self.verbose)
            self.log.debug(f'RESULT: metric: {metric_name}; score = {cached_result}; type = {type(cached_result)}.', verbose=self.verbose)
        else:
            self.log.debug("Cache Miss!", verbose=self.verbose)
            cache_hit = False

        return cache_hit, output

    def cache_score(self, metric_name, result, **kwargs) -> None:
        self.log.debug("Saving value to cache!", verbose=self.verbose)
        cache_key = self.get_cache_key(metric_name, **kwargs)
        self.cachekv.save_value(value=result, key=cache_key)

    async def perform(self, metric_name, **kwargs) -> float:
        self.log.debug("START Scoring...", verbose=self.verbose)
        self.log.debug(f"* METRIC_NAME: {metric_name}", verbose=self.verbose)
        self.log.debug(f"* USER_INPUT: {kwargs.get('user_input', None)}", verbose=self.verbose)
        self.log.debug(f"* REFERENCE: {kwargs.get('reference', None)}", verbose=self.verbose)
        self.log.debug(f"* RESPONSE: {kwargs.get('response', None)}",verbose=self.verbose)
        self.log.debug(f"* RETRIEVED_CONTEXTS: {kwargs.get('retrieved_contexts', None)}",verbose=self.verbose)

        score = None
        s_time = time()
        if metric_name == 'response_groundedness':
            score = await self.AVAILABLE_METRICS_MAP[metric_name](
                response=kwargs['response'], retrieved_contexts=kwargs['retrieved_contexts'])
        elif metric_name == 'context_relevance':
             score = await self.AVAILABLE_METRICS_MAP[metric_name](
                 user_input=kwargs['user_input'], retrieved_contexts=kwargs['retrieved_contexts'])
        elif metric_name == 'faithfulness':
            score = await self.AVAILABLE_METRICS_MAP[metric_name](
                user_input=kwargs['user_input'], response=kwargs['response'],
                retrieved_contexts=kwargs['retrieved_contexts'])
        elif metric_name == 'context_entity_recall':
            score = await self.AVAILABLE_METRICS_MAP[metric_name](
                reference=kwargs['reference'], retrieved_contexts=kwargs['retrieved_contexts'])
        else:
            raise ValueError
        e_time = time()

        self.log.debug(f'RESULT: metric: {metric_name}; score = {score}; type = {type(score)}; elapsed_time = {round(e_time-s_time,5)}.', verbose=self.verbose)

        return score