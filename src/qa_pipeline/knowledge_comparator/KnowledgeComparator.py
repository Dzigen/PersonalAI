from .utils import KnowledgeComparatorConfig
from ...neo4j_functions import Neo4jConnection
from ..query_parser.utils import ParsedQueryStructure

class KnowledgeComparator:
    def __init__(self, config: KnowledgeComparatorConfig, kg_model) -> None:
        self.config = config

    def link_kgnodes_to_query(self, query_structure: ParsedQueryStructure):
        # сопостовляем сущности, извлечённые из запроса нодам в графе знаний
        pass