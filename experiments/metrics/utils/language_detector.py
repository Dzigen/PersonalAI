from lingua import LanguageDetectorBuilder
from typing import Tuple

from .errors import ReturnStatus

SUPPORTED_LANGUAGES_MAP = {'RUSSIAN': 'ru', 'ENGLISH': 'en'}
DETECTOR = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()


def detect_lang(text: str) -> Tuple[str, str, ReturnStatus]:
    """Функция предназначена для определения доминирующего языка, который используется во входном тексте.

    :param text: Текст, для которого требуется определить язык.
    :type text: str
    :return: Кортеж из трёх объектов: (1) поддерживаемый язык в краткой нотации; (2) предсказанный язык; (3) статус завершения операции с пояснительной информацией.
    :rtype: Tuple[str, ReturnStatus]
    """
    supported_lang, predicted_lang, status = None, None, ReturnStatus.success
    if len(text) == 0:
        status = ReturnStatus.empty_input_text

    if status == ReturnStatus.success:
        predicted_lang = DETECTOR.detect_language_of(text).name
        supported_lang = SUPPORTED_LANGUAGES_MAP.get(predicted_lang, None)

    if (status == ReturnStatus.success) and (supported_lang is None):
        status = ReturnStatus.not_supported_lang

    return supported_lang, predicted_lang, status
