from typing import Dict
import torch
from transformers import pipeline

from ..utils import AbstractAgentConnector, AgentConnectorConfig

DEFAULT_LOCALAGENT_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_new_tokens': 2048},
    credentials={'model_name_or_path': '../models/Undi95/Meta-Llama-3-8B-Instruct-hf'},
    ext_params={'num_workers': 4, 'torch_dtype': torch.bfloat16})

class LocalAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_LOCALAGENT_CONFIG) -> None:
        self.config = config
        self.pipeline = pipeline(
            "text-generation",
            model=self.config.credentials['model_name_or_path'],
            model_kwargs={"torch_dtype": self.config.ext_params['torch_dtype']},
            device_map="auto"
        )

    def check_connection(self):
        pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        """_summary_

        :param system_prompt: _description_
        :type system_prompt: str
        :param user_prompt: _description_
        :type user_prompt: str
        :param assistant_prompt: _description_, defaults to None
        :type assistant_prompt: str, optional
        :return: _description_
        :rtype: str
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user","content": user_prompt}]

        if assistant_prompt is not None:
            messages.insert(1, {"role": "assistant", "content": assistant_prompt})

        prompt = self.pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy

        outputs = self.pipeline(
            prompt,
            eos_token_id=terminators,
            pad_token_id=self.pipeline.tokenizer.eos_token_id,
            return_full_text=False,
            **gen_strategy
        )

        return outputs[0]["generated_text"]
