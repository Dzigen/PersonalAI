from .utils import AbstractAgentModel

from dataclasses import dataclass, field
from typing import Dict
import torch
from transformers import pipeline

SYSTEM_PROMPT = "You are a helpful assistant."

@dataclass
class AgentModelConfig:
    gen_strategy: Dict = field(default_factory=lambda: {'early_stopping': True, 'num_beams': 3, 'max_new_tokens': 2048})
    model_name_or_path: str = "/app/models/Undi95/Meta-Llama-3-8B-Instruct-hf"
    system_prompt: str = SYSTEM_PROMPT
    num_workers: int = 4

class AgentModel(AbstractAgentModel):
    def __init__(self, config: AgentModelConfig = AgentModelConfig()) -> None:
        self.config = config
        self.pipeline = pipeline(
            "text-generation",
            model=self.config.model_name_or_path,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        )

    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None) -> str:
        """Метод для генерации ответов на текстовые запросы с помощью llm-агента.

        Args:
            user_prompt (str): Запрос для llm-агента.
            assistant_prompt (str, optional): Дополнительная к user_prompt-запросу информация, 
                                              которая может быть использована llm-агентом при генерации ответа. Defaults to None.
            gen_strategy (Dict, optional): Стретегия генерации текстовой последовательности для llm-агента. Defaults to None.

        Returns:
            str: Текстовая последовательность, сгенерированная llm-агентом.
        """
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user","content": user_prompt}
            ]

        if assistant_prompt is not None:
            messages.insert(1, {"role": "assistant", "content": assistant_prompt})

        prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
        )

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy
        
        outputs = self.pipeline(
            prompt,
            eos_token_id=terminators,
            **gen_strategy
        )
        
        return outputs[0]["generated_text"][len(prompt):]