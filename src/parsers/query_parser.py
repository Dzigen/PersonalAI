from typing import List, Tuple

from ..utils import ReturnStatus

def qa_custom_entities_parse_func(raw_response: str) -> Tuple[List[str], ReturnStatus]:
    """_summary_

    :param raw_response: _description_
    :type raw_response: str
    :return: _description_
    :rtype: Tuple[List[str], ReturnStatus]
    """
    entities = list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_response.split('|')))))
    return entities, ReturnStatus.success
