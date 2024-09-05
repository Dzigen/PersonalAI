from dataclasses import dataclass

@dataclass
class EntitiesExtractorConfig:
    system_prompt: str
    assistant_prompt: str
    user_prompt: str

@dataclass
class QueryLLMParserConfig:
    ents_extr_config: EntitiesExtractorConfig


@dataclass
class ParsedQuery:
    pass

