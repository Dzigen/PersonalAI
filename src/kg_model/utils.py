from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class KGEmbeddersMapping:
    """Отображение компонент моделей графа на имена эмбеддеров.

    :param embeddings_model: Словарь, задающий соответствие логических компонент модели графа (например, 'nodes_dense', 'triplets_dense') именам эмбеддеров, настроенных в DEFAULT_EMBEDDERS_CONFIG или в пользовательской конфигурации. Значение по умолчанию None.
    :type embeddings_model: Union[None, Dict[str, str]]
    :param nodestree_model: Словарь, задающий соответствие компонент nodestree-модели именам эмбеддеров, настроенных в DEFAULT_EMBEDDERS_CONFIG или в пользовательской конфигурации. Значение по умолчанию None.
    :type nodestree_model: Union[None, Dict[str, str]]
    """
    embeddings_model: Union[None, Dict[str, str]] = None
    nodestree_model: Union[None, Dict[str, str]] = None


@dataclass
class AgentsMapping:
    """Отображение пайплайнов на выбранные агентные драйверы.

    :param qa_pipeline: Имя агентного драйвера, используемого в QA-пайплайне.
    :type qa_pipeline: str
    :param mem_pipeline: Имя агентного драйвера, используемого в memorize-пайплайне.
    :type mem_pipeline: str
    :param kg_nodestree_model: Имя агентного драйвера, используемого в nodestree-модели. Значение по умолчанию None.
    :type kg_nodestree_model: Union[None, str]
    """
    qa_pipeline: str
    mem_pipeline: str
    kg_nodestree_model: Union[None, str] = None
