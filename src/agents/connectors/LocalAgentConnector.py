from transformers import pipeline
from typing import Union, Dict, Tuple
import gc
from time import time

from .configs import DEFAULT_LOCALAGENT_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig, LLMInferenceStat


class LocalAgentConnector(AbstractAgentConnector):
    def __init__(self, config: Union[Dict, AgentConnectorConfig] = DEFAULT_LOCALAGENT_CONFIG) -> None:
        if isinstance(config, dict):
            config = AgentConnectorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: AgentConnectorConfig = config

        self.CONNECTOR_KW = 'local'

        self.pipeline = pipeline(
            "text-generation",
            model=self.config.credentials['model_name_or_path'],
            model_kwargs={"torch_dtype": self.config.credentials['torch_dtype']},
            device_map="auto"
        )

    def check_connection(self):
        # TODO
        pass

    def close_connection(self):
        del self.pipeline
        gc.collect()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

        if assistant_prompt is not None:
            messages.insert(
                1, {"role": "assistant", "content": assistant_prompt})

        prompt = self.pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy

        ai_start_time = time()
        outputs = self.pipeline(
            prompt,
            eos_token_id=terminators,
            pad_token_id=self.pipeline.tokenizer.eos_token_id,
            return_full_text=False,
            **gen_strategy
        )
        ai_end_time = time()

        inference_info = LLMInferenceStat(
            prompt_tokens_amount=len(self.pipeline.tokenizer.tokenize(prompt)),
            generated_tokens_amount=len(self.pipeline.tokenizer.tokenize(outputs[0]["generated_text"])),
            inference_elapsed_time=round(ai_end_time - ai_start_time, 2)
        )

        return outputs[0]["generated_text"], inference_info

    def __del__(self):
        self.close_connection()
