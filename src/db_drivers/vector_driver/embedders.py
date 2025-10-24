from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Union


@dataclass
class EmbedderModelConfig:
    model_name_or_path: str = '../models/intfloat/multilingual-e5-small'
    prompts: Union[None, Dict] = field(default_factory=lambda: {
        "query": "query: ", "passage": "passage: "})
    query_prompt_name: Union[None, str] = 'query'
    passage_prompt_name: Union[None, str] = 'passage'
    device: str = 'cuda'
    normalize_embeddings: bool = True


class EmbedderModel:

    def __init__(self, config: EmbedderModelConfig = None) -> None:
        self.config = EmbedderModelConfig() if config is None else config
        parameters = {
            'model_name_or_path': config.model_name_or_path,
            'device': config.device,
        }
        if (self.config.prompts is not None) and (len(self.config.prompts) > 0):
            parameters['prompts'] = self.config.prompts

        self.model = SentenceTransformer(**parameters)

    def encode(self, queries: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(
            queries, normalize_embeddings=self.config.normalize_embeddings, **kwargs)
        return [list(obj.astype(float)) for obj in output]

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(queries, prompt_name=self.config.query_prompt_name,
                                   normalize_embeddings=self.config.normalize_embeddings, **kwargs)
        return [list(obj.astype(float)) for obj in output]

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(passages, prompt_name=self.config.passage_prompt_name,
                                   normalize_embeddings=self.config.normalize_embeddings,
                                   **kwargs)
        return [list(obj.astype(float)) for obj in output]
