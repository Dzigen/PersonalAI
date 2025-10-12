from typing import List, Union, Tuple
from abc import ABC, abstractmethod
from ...db_drivers.vector_driver import VectorDBInstance


class AbstractRerankerModule(ABC):

    @abstractmethod
    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: bool = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        """_summary_

        :param query: _description_
        :type query: str
        :param top_k: _description_, defaults to 1
        :type top_k: int, optional
        :param subset_ids: _description_, defaults to None
        :type subset_ids: Union[None, List[str]], optional
        :param includes: _description_, defaults to ['documents', 'metadatas']
        :type includes: List[str], optional
        :param return_with_embeddings: _description_, defaults to False
        :type return_with_embeddings: Union[str, bool], optional
        :param return_with_scores: _description_, defaults to False
        :type return_with_scores: Union[str, bool], optional
        :return: _description_
        :rtype: Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]
        """
        pass
