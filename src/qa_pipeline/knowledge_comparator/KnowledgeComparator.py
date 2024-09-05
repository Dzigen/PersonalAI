from .utils import KnowledgeComparatorConfig
from ...neo4j_functions import Neo4jConnection

class KnowledgeComparator:
    def __init__(self, config: KnowledgeComparatorConfig, kg_model) -> None:
        pass

    def link_entities_to_nodes(self):
        # сопостовляем сущности, извлечённые из запроса нодам в графе знаний
        pass