from dataclasses import dataclass
from .db_models.graph_db.neo4j_functions import Neo4jConnection
from .db_models.embeddings_db.embedding_functions import EmbeddingsDatabaseConnection

@dataclass
class KnowledgeGraphModel:
    graph_db: Neo4jConnection
    embeddings_db: EmbeddingsDatabaseConnection