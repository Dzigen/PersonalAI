from abc import abstractmethod, ABC
import torch
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Union
from copy import deepcopy

from ..utils import AbstractDatabaseConnection, AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class VectorDBConnectionConfig(BaseDatabaseConfig):
    """Конфигурация подключения к векторной БД (dense/sparse).

    :param db_info: Информация о БД и коллекции/таблице. По умолчанию {'db': 'defaultpersonalaivectordb', 'table': 'defaultpersonalaivectortable'}.
    :type db_info: Dict
    :param conn: Дополнительные параметры подключения к конкретному векторному движку.
    :type conn: Dict
    """
    db_info: Dict = field(default_factory=lambda: {'db': 'defaultpersonalaivectordb', 'table': 'defaultpersonalaivectortable'})
    conn: Dict = field(default_factory=lambda: dict())

    def to_str(self):
        str_needto = f"{self.need_to_clear};{self.create_index}"
        return f"{self.db_info};{str_needto};{self.params};{self.conn}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = VectorDBConnectionConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


@dataclass
class VectorDBInstance:
    """Контейнер для представления одной записи в векторном хранилище.

    :param id: Уникальный идентификатор объекта (строка) либо None, если идентификатор ещё не задан.
    :type id: Union[None, str]
    :param document: Текст документа, соответствующий вектору, либо None.
    :type document: Union[None, str]
    :param embedding: Векторное представление документа (список float) либо None.
    :type embedding: Union[None, List[float]]
    :param metadata: Словарь с произвольной дополнительной информацией об объекте.
    :type metadata: Dict
    """
    id: Union[None, str] = None
    document: Union[None, str] = None
    embedding: Union[None, List[float]] = None
    metadata: Dict = field(default_factory=lambda: dict())

    def to_dict(self):
        return {k: v for k, v in asdict(self).items()}


class AbstractVectorDatabaseConnection(AbstractDatabaseConnection):
    """Абстрактный интерфейс для взаимодействия с векторным хранилищем.

    Определяет базовые операции для:
     - извлечения ближайших по метрике объектов (retrieve),
     - upsert (создания/обновления) векторных объектов,
     - проверки корректности аргументов запросов.
    """
    @abstractmethod
    def retrieve(self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
                 includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        """Метод предназначен для извлечения N ближайших объектов к заданным запросам по заданной метрике.

        :param query_instances: Список запросов, представленных в виде VectorDBInstance.
        :type query_instances: List[VectorDBInstance]
        :param n_results: Количество ближайших объектов, которое требуется вернуть для каждого запроса.
        :type n_results: int
        :param subset_ids: Ограничение поиска заданным подмножеством идентификаторов.
        :type subset_ids: Union[None, List[str]]
        :param includes: Список полей, которые необходимо возвращать для каждого найденного объекта.
        :type includes: List[str]
        :return: Для каждого запроса возвращается список пар (score, VectorDBInstance) с найденными объектами.
        :rtype: List[List[Tuple[float, VectorDBInstance]]]
        """
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        """Метод предназначен для создания или обновления записей в векторном хранилище.

        :param items: Список объектов, подлежащих сохранению или обновлению.
        :type items: List[VectorDBInstance]
        """
        pass

    def validate_retrieve_arguments(
            self, query_instances: List[VectorDBInstance], n_results: int,
            subset_ids: Union[None, List[str]], includes: List[str]) -> bool:
        """Метод предназначен для валидации аргументов запроса retrieve.

        :param query_instances: Список запросов для векторного поиска.
        :type query_instances: List[VectorDBInstance]
        :param n_results: Количество ближайших объектов на каждый запрос.
        :type n_results: int
        :param subset_ids: Ограничивающее множество идентификаторов или None.
        :type subset_ids: Union[None, List[str]]
        :param includes: Список названий полей, которые необходимо вернуть.
        :type includes: List[str]
        :return: True, если все аргументы корректны, иначе - исключение.
        :rtype: bool
        """
        if len(query_instances) < 1:
            return ValueError

        if not isinstance(n_results, int):
            raise TypeError(f"n_results: {n_results}")
        elif n_results < 0:
            raise ValueError(f"n_results: {n_results}")

        for inst in query_instances:
            if type(inst.embedding) in [torch.Tensor, np.ndarray]:
                raise ValueError(f"inst: {inst}")

        if isinstance(includes, list):
            for name in includes:
                if not ((isinstance(name, str)) and (name in ['documents', 'metadatas', 'embeddings'])):
                    raise ValueError(f"includes: {includes}")

        if isinstance(subset_ids, list):
            for cur_id in subset_ids:
                assert isinstance(cur_id, str)
        elif subset_ids is not None:
            raise ValueError(f"subset_ids: {subset_ids}")


class AbstractVectorDatabaseComposer(AbstractDatabaseConnection):
    """Абстрактный интерфейс для компоновщика нескольких векторных хранилищ."""
    @abstractmethod
    def check_consistency(self) -> bool:
        """Метод предназначен для проверки консистентности данных между всеми подключёнными векторными хранилищами."""
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        """Метод предназначен для выполнения upsert'a в нескольких векторных хранилищах одновременно."""
        pass
