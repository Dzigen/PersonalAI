from enum import Enum
from dataclasses import dataclass

class ReturnStatus(Enum):
    success = 0
    warning = 1
    error = 2
    bad_format = 3
    zero_triplets = 4
    zero_entities = 5
    zero_linked_nodes = 6
    zero_retrieved_triplets = 7

@dataclass
class ReturnInfo:
    status: ReturnStatus = ReturnStatus.success
    message: str = ""

MEM_BAD_TRIPLET_EXTRACTION_PROMPT = ''

MEM_BAD_THESIS_EXTRACTION_PROMPT = ''

MEM_ZERO_EXTRACTED_TRIPLETS_MSG = ''

QA_ZERO_ENTITIES_MSG = ''

QA_BAD_ENTITIES_EXTRACTION_PROMPT = ''

QA_ZERO_LINKED_NODES_MSG = ''

QA_ZERO_RETRIEVED_TRIPLETS_MSG = ''
