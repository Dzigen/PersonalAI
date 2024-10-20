from polyglot.detect import Detector

def detect_lang(text: str) -> str:
    return Detector(text).languages[0].code