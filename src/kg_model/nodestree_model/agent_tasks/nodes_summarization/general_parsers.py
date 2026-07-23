from typing import Dict


def summn_custom_formate(n_descendants: str, new_content: str,
                         current_content: str) -> Dict[str, str]:
    """Метод предназначен для подготовки контекста суммаризации в формате словаря параметров.

    :param n_descendants: Количество предыдущих записей, резюме которых представлено в current_content.
    :type n_descendants: str
    :param new_content: Новая информация, которая должна быть учтена в резюме.
    :type new_content: str
    :param current_content: Текущее резюме по предыдущим записям.
    :type current_content: str
    :return: Словарь с параметрами, передаваемыми в промпт суммаризации.
    :rtype: Dict[str, str]
    """
    if len(new_content) < 1 or len(current_content) < 1:
        raise ValueError(f"* new_content: {new_content}\n* len(current_content): {len(current_content)}\n* current_content: {current_content}")
    if int(n_descendants) < 0:
        raise ValueError(f"n_descendants: {n_descendants}")

    return {'n_descendants': n_descendants, 'new_content': new_content,
            'current_content': current_content}


def summn_custom_postprocess(parsed_summary: str, **kwargs) -> str:
    """Метод предназначен для постобработки результата суммаризации.

    :param parsed_summary: Результат суммаризации, полученный от LLM.
    :type parsed_summary: str
    :return: Финальное отфильтрованное резюме.
    :rtype: str
    """
    if len(parsed_summary) < 1:
        raise ValueError(f"parsed_response: '{parsed_summary}'")
    return parsed_summary
