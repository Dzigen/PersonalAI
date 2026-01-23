from lingua import LanguageDetectorBuilder
from typing import Tuple

from .errors import ReturnStatus

SUPPORTED_LANGUAGES_MAP = {'RUSSIAN': 'ru', 'ENGLISH': 'en'}
DETECTOR = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()


def detect_lang(text: str) -> Tuple[str, ReturnStatus]:
    """Функция предназначена для определения доминирующего языка, который используется во входном тексте.

    :param text: Текст, для которого требуется определить язык.
    :type text: str
    :return: Кортеж из двух объектов: (1) язык в краткой нотации; (2) статус завершения операции с пояснительной информацией.
    :rtype: Tuple[str, ReturnStatus]
    """
    lang, status = None, ReturnStatus.success
    if len(text) == 0:
        status = ReturnStatus.empty_input_text

    if status == ReturnStatus.success:
        language = DETECTOR.detect_language_of(text).name
        lang = SUPPORTED_LANGUAGES_MAP.get(language, None)

    if (status == ReturnStatus.success) and (lang is None):
        status = None, ReturnStatus.not_supported_lang

    return lang, status
