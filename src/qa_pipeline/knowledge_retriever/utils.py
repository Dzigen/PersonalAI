from dataclasses import dataclass
from enum import Enum
from ...retrieve.astar import AStarGraphSearchConfig

class GraphSearchMethods(Enum):
    astar = "astar"

@dataclass
class KnowledgeRetrieverConfig:
    graph_search_method: str 
    graph_search_config: object