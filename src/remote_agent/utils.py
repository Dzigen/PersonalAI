from dataclasses import dataclass
from enum import Enum
from typing import List
from abc import ABC, abstractmethod

class AbstractAgentConnector:
    @abstractmethod
    def open_connection(self):
        pass

    @abstractmethod
    def close_connection(self):
        pass

    @abstractmethod
    def generate(self):
        pass

class AbstractAgentModel:
    @abstractmethod
    def generate(self):
        pass