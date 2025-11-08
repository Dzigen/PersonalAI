from abc import abstractmethod, ABC
import torch
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Union

from ..utils import AbstractDatabaseConnection, AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class VectorDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {'db': 'defaultpersonalaivectordb', 'table': 'defaultpersonalaivectortable'})
    conn: Dict = field(default_factory=lambda: dict())

    def to_str(self):
        str_needto = f"{self.need_to_clear};{self.create_index}"
        return f"{self.db_info};{str_needto};{self.params};{self.conn}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = VectorDBConnectionConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config


@dataclass
class VectorDBInstance:
    id: Union[None, str] = None
    document: Union[None, str] = None
    embedding: Union[None, List[float]] = None
    metadata: Dict = field(default_factory=lambda: dict())

    def to_dict(self):
        return {k: v for k, v in asdict(self).items()}


class AbstractVectorDatabaseConnection(AbstractDatabaseConnection):
    @abstractmethod
    def retrieve(self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
                 includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        pass

    def validate_retrieve_arguments(
            self, query_instances: List[VectorDBInstance], n_results: int,
            subset_ids: Union[None, List[str]], includes: List[str]) -> bool:
        if len(query_instances) < 1:
            return ValueError

        if not isinstance(n_results, int):
            raise TypeError
        elif n_results < 0:
            raise ValueError

        for inst in query_instances:
            if type(inst.embedding) in [torch.Tensor, np.ndarray]:
                raise ValueError

        if isinstance(includes, list):
            for name in includes:
                if not ((isinstance(name, str)) and (name in ['documents', 'metadatas', 'embeddings'])):
                    raise ValueError

        if isinstance(subset_ids, list):
            for cur_id in subset_ids:
                assert isinstance(cur_id, str)
        elif subset_ids is not None:
            raise ValueError


class AbstractVectorDatabaseComposer(AbstractDatabaseConnection):

    @abstractmethod
    def check_consistency(self) -> bool:
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        pass
