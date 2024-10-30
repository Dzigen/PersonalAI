from polyglot.detect import Detector
from typing import Tuple

from .errors import ReturnStatus

SUPPORTED_LANGUAGES = {'ru', 'en'}

def detect_lang(text: str) -> Tuple[str, ReturnStatus]:
    status = ReturnStatus.success
    lang = Detector(text).languages[0].code
    if lang not in SUPPORTED_LANGUAGES:
        status = ReturnStatus.not_supported_lang

    return lang, status
