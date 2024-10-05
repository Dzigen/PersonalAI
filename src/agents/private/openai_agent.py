from ..utils import SYSTEM_PROMPT

import os 
from typing import Dict
from openai import OpenAI 

API_KEY = "sk-861mINAavom2SSBqgrI82D4thMOfqT37knCof2o0H0T3BlbkFJ2gdVXJuVjNesNNP2aeUwPoBpZP3a3R1gn1kqv97CsA"

class OpenAIAgent:
    def __init__(self, api_key: str = API_KEY, model: str = 'gpt-4o-mini') -> None:
        self.model = model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key))

    def generate(self, user_prompt: str, assistant_prompt: str = None, 
                 system_prompt: str = None, gen_strategy: Dict = None) -> str:
        messages = [
            {"role": "system", "content": system_prompt if system_prompt is not None else SYSTEM_PROMPT},
            {"role": "user","content": user_prompt}]

        if assistant_prompt is not None:
            messages.insert(1, {"role": "assistant", "content": assistant_prompt})

        completion = self.client.chat.completions.create(
            model=self.model, messages=messages)

        return completion.choices[0].message.content