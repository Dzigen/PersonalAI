import os
import sys
import picologging as logging
import picologging.handlers
from typing import Union
from dataclasses import dataclass, fields
import functools
from time import time
import hashlib
import queue
import atexit


@dataclass
class LogLevel:
    NOTSET: int = 0
    DEBUG: int = 10
    INFO: int = 20
    WARNING: int = 30
    ERROR: int = 40
    CRITICAL: int = 50
    DISABLED: int = 51


def modify_log_setting(func):
    @functools.wraps(func)
    def wrapper(self, text: str, *args, verbose: bool = False, log_level: LogLevel = LogLevel.DEBUG):

        # print(verbose, log_level)
        self.stream_handler.setLevel(LogLevel.DISABLED if not verbose else log_level)
        self.file_handler.setLevel(log_level)
        # self.queue_handler.setLevel(log_level)

        # print(self.stream_handler.level, self.file_handler.level, self.queue_handler.level)

        func(self, text, *args)

    return wrapper


class Logger:
    def __init__(self, path, name: Union[str, None] = None):
        self.path = path
        os.makedirs(path, exist_ok=True)

        self.logger = logging.getLogger(self.create_id() if name is None else name)
        self.logger.setLevel(LogLevel.DEBUG)

        self.log_queue = queue.Queue(-1)
        self.queue_handler = logging.handlers.QueueHandler(self.log_queue)
        self.queue_handler.setLevel(LogLevel.DEBUG)
        self.logger.addHandler(self.queue_handler)

        custom_date_format = '%m/%d/%Y %H:%M:%S'
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt=custom_date_format)

        self.file_handler = logging.FileHandler(f"{path}/.log", mode='a')
        self.file_handler.setLevel(LogLevel.DEBUG)
        self.file_handler.setFormatter(formatter)

        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setLevel(LogLevel.DEBUG)
        self.stream_handler.setFormatter(formatter)

        # self.logger.propagate = False

        listener = logging.handlers.QueueListener(
            self.log_queue, self.file_handler, self.stream_handler,
            respect_handler_level=True)
        listener.start()
        atexit.register(listener.stop)

    def __del__(self):
        try:
            self.stream_handler.close() 
            self.file_handler.close()
            self.logger.removeHandler(self.stream_handler)
            self.logger.removeHandler(self.file_handler)
        except AttributeError:
            pass

    def create_id(self, seed: Union[None, str] = None) -> str:
        if seed is None:
            seed = f"{time()}"
        return hashlib.md5(seed.encode()).hexdigest()

    @modify_log_setting
    def info(self, text: str, *args):
        self.logger.info(text, *args)

    @modify_log_setting
    def warning(self, text: str, *args):
        self.logger.warning(text, *args)

    @modify_log_setting
    def debug(self, text: str, *args):
        self.logger.debug(text, *args)

    @modify_log_setting
    def critical(self, text: str, *args):
        self.logger.critical(text, *args)

    @modify_log_setting
    def error(self, text: str, *args):
        self.logger.error(text, *args)
