from dataclasses import dataclass


@dataclass
class KnowledgeComparatorConfig:
    threshold: float = 0.5
    fetch_n: int = 20
    max_k: int = 1