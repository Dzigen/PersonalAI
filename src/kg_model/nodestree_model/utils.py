from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TreeNodeType(Enum):
    leaf = "leaf"
    root = "root"
    summarized = "summarized"

@dataclass
class TreeNode:
    id: str
    text: str
    type: TreeNodeType
    props: Dict[str, object]
