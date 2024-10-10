from dataclasses import dataclass

# TODO
class EmbeddingsModel:
    pass

# TODO
class GraphModel:
    pass

@dataclass
class KnowledgeGraphModel:
    graph_struct: GraphModel
    embeddings_struct: EmbeddingsModel
