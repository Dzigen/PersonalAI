from typing import List, Tuple, Dict
import gc
import joblib
import os
import time
import hashlib

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection

# TODO
DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig()

# TODO
class InMemoryGraphConnector(AbstractGraphDatabaseConnection):
    pass