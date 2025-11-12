from dataclasses import dataclass
from ..utils import BaseStages
from .answers_aggregation import AnswersAggregator
from .kg_reasoning import KnowledgeGraphReasoner
from .query_preprocessing import QueryPreprocessor


@dataclass
class QAPipelineStages(BaseStages):
    query_preprocessor: QueryPreprocessor
    kg_reasoner: KnowledgeGraphReasoner
    answers_aggregator: AnswersAggregator
