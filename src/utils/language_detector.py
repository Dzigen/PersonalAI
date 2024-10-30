from polyglot.detect import Detector
from polyglot.detect.base import UnknownLanguage 
from typing import Tuple

from .errors import ReturnStatus

SUPPORTED_LANGUAGES = {'ru', 'en'}

def detect_lang(text: str) -> Tuple[str, ReturnStatus]:
    lang, status = None, ReturnStatus.success
    if len(text) == 0:
        status = ReturnStatus.empty_input_text
    
    if status == ReturnStatus.success:
        try:
            lang = Detector(text).languages[0].code
        except UnknownLanguage as e:
            status = ReturnStatus.unknown_lang
    
    if (status == ReturnStatus.success) and (lang not in SUPPORTED_LANGUAGES):
        status = ReturnStatus.not_supported_lang

    return lang, status
