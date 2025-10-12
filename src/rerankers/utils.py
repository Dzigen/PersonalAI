from dataclasses import dataclass


@dataclass
class BaseRerankerModuleConfig:
    pass

    def to_str(self) -> str:
        pass
