import os
import sys
import json
import logging
import torch
import datetime
from dataclasses import dataclass

@dataclass
class LogLevel:
    NOTSET: int = 0
    DEBUG: int = 10
    INFO: int = 20
    WARNING: int = 30
    ERROR: int = 40
    CRITICAL: int = 50
    DISABLED: int = 51

class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def __call__(self, text, filename="log.txt", verbose=True, debug=True):
        if debug:
            text = str(text)
            if verbose:
                print(text)
            with open(self.path + "/" + filename, "a") as file:
                file.write(f"[{str(datetime.datetime.now())}] {text}\n")

    def to_json(self, obj, filename="history.json"):
        try:
            with open(self.path + "/" + filename, "w") as file:
                json.dump(obj, file)
        except BaseException:
            raise "Object isn't json serializible"
