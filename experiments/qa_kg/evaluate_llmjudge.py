
import sys
from tqdm import tqdm
import yaml
import os
import json
import numpy as np
from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance
from typing import Dict
import torch
import gc
import os


import nltk
nltk.download('wordnet')

################LOADING_HYPERPARAMETERS###################

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)
