from dataclasses import dataclass
from enum import Enum
from ....utils import BaseStages

from .answer_generator import AnswerGenerator
from .clueanswer_generator import ClueAnswerGenerator
from .clueanswers_summarisation import ClueAnswersSummarizer
from .entities2nodes_matching import Entities2NodesMatcher
from .entities_extractor import EntitiesExtractor
from .searchplan_enhancer import SearchPlanEnhancer
from .cluequeries_generator import ClueQueriesGenerator
from ..weak_reasoner.knowledge_retriever import KnowledgeRetriever


@dataclass
class MediumKGReasonerStages(BaseStages):
    searchplan_enhancer: SearchPlanEnhancer
    entities_extractor: EntitiesExtractor
    entities2nodes_matcher: Entities2NodesMatcher
    cluequeries_generator: ClueQueriesGenerator
    knowledge_retriever: KnowledgeRetriever
    clueanswer_generator: ClueAnswerGenerator
    clueanswers_summarizer: ClueAnswersSummarizer
    answer_generator: AnswerGenerator


class RelInfoFoundBehaviour(Enum):
    casual_answer = 'casual_answer'
    strict_answer = 'strict_answer'


class PlanLimitExceededBehaviour(Enum):
    casual_answer = 'casual_answer'
    strict_answer = 'strict_answer'
    noanswer_stub = 'noanswer_stub'
