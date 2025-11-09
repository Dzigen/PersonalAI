from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Union
from langchain_core.embeddings.embeddings import Embeddings
from copy import deepcopy

from ...utils.data_structs import BaseConfigOperations


@dataclass
class EmbedderModelConfig(BaseConfigOperations):
    model_name_or_path: str = '../models/intfloat/multilingual-e5-small'
    prompts: Union[None, Dict] = field(default_factory=lambda: {
        "query": "query: ", "passage": "passage: "})
    query_prompt_name: Union[None, str] = 'query'
    passage_prompt_name: Union[None, str] = 'passage'
    device: str = 'cuda'
    normalize_embeddings: bool = True

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = EmbedderModelConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        pass


class EmbedderModel(Embeddings):

    def __init__(self, config: Union[EmbedderModelConfig, Dict, None] = None) -> None:
        if isinstance(config, dict):
            config: EmbedderModelConfig = EmbedderModelConfig.from_dict(config)
        elif config is not None:
            config.formate_fields()
        self.config = EmbedderModelConfig() if config is None else config

        parameters = {
            'model_name_or_path': config.model_name_or_path,
            'device': config.device,
        }
        if (self.config.prompts is not None) and (len(self.config.prompts) > 0):
            parameters['prompts'] = self.config.prompts

        self.model = SentenceTransformer(**parameters)

    def encode(self, text: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(
            text, normalize_embeddings=self.config.normalize_embeddings, **kwargs)
        return [list(obj.astype(float)) for obj in output]

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(queries, prompt_name=self.config.query_prompt_name,
                                   normalize_embeddings=self.config.normalize_embeddings, **kwargs)
        return [list(obj.astype(float)) for obj in output]

    def embed_query(self, text: str) -> List[float]:
        return self.encode_queries([text])

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        output = self.model.encode(passages, prompt_name=self.config.passage_prompt_name,
                                   normalize_embeddings=self.config.normalize_embeddings,
                                   **kwargs)
        return [list(obj.astype(float)) for obj in output]

    def embed_documents(self, texts: list[str]) -> List[List[float]]:
        return self.encode_passages(texts)
