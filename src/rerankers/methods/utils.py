from typing import List, Union, Tuple
from abc import ABC, abstractmethod
from ...db_drivers.vector_driver import VectorDBInstance


class AbstractRerankerModule(ABC):

    @abstractmethod
    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: bool = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        """Метод предназначен для запуска/выполнения логики заданного Retrieve/Rerank-оператора.

        :param query: Текст/запрос на естественном языке для извлечения релевантных элементов на его основе.
        :type query: str
        :param top_k: Максимальное количество извлекаемых элементов. Значение по умочланию 1.
        :type top_k: int, optional
        :param subset_ids: Подмножество идентификаторов элементов, в рамках которого нужно искать релевантные элементы. Значение по умолчанию None.
        :type subset_ids: Union[None, List[str]], optional
        :param includes: Названия полей в возвращаемых релевантных элементах, которые должны быть заполнены. Значения по умолчанию ['documents', 'metadatas'].
        :type includes: List[str], optional
        :param return_with_embeddings: Если True, то в структурах данных возвращаемых релевантных элементов будет содержаться их векторные представления. Значение по умолчанию False.
        :type return_with_embeddings: Union[str, bool], optional
        :param return_with_scores: Если True, то возвращаемым релевантным элементам будет сопоставлена их similarity-оценка к запросу, иначе False. Значение по умолчанию False.
        :type return_with_scores: Union[str, bool], optional
        :return: Релевантный набор элементов к заданному запросу.
        :rtype: Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]
        """
        pass
