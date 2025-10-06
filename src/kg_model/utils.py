from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class KGEmbeddersMapping:
    embeddings_model: Union[None, Dict[str, str]] = None
    nodestree_model: Union[None, str] = None


@dataclass
class AgentsMapping:
    qa_pipeline: str
    mem_pipeline: str
    kg_nodestree_model: Union[None, str] = None
