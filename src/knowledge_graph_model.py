from dataclasses import dataclass
from .neo4j_functions import Neo4jConnection
from .embedding_functions import EmbeddingsDatabaseConnection

@dataclass
class KnowledgeGraphModel:
    graph_db: Neo4jConnection
    embeddings_db: EmbeddingsDatabaseConnection