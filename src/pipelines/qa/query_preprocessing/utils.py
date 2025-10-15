from dataclasses import dataclass, field
from typing import Union, List

from dataclasses import dataclass

from ...utils import BaseStages
from .decomposition import QueryDecomposer
from .enhancing import QueryEnhancer
from .denoising import QueryDenoiser


@dataclass
class QueryPreprocessingStages(BaseStages):
    denoiser: Union[None, QueryDenoiser] = None
    enhancer: Union[None, QueryEnhancer] = None
    decomposer: Union[None, QueryDecomposer] = None
