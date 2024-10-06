from ..utils import SYSTEM_PROMPT

import os
from typing import Dict
from gigachat import GigaChat 
from gigachat.models import Chat, Messages 

GIGACHAT_CREDS = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='

class GigaChatAgent:
    def __init__(self, creds: str = GIGACHAT_CREDS, scope: str = 'GIGACHAT_API_CORP', model: str = "GigaChat-Pro",
                 verify_ssl_certs: bool = False) -> None:
        self.giga_model = GigaChat(
            credentials=creds, scope=scope, verify_ssl_certs=verify_ssl_certs, model=model) 
        
    def generate(self, user_prompt: str, assistant_prompt: str = None, 
                 system_prompt: str = None, gen_strategy: Dict = {'temperature': 0.001}) -> str:
        chat = Chat(messages=[Messages(role='system', content=system_prompt if system_prompt is not None else SYSTEM_PROMPT), 
                            Messages(role='user', content=user_prompt)], **gen_strategy) 
        response = self.giga_model.chat(chat) 
        return response.choices[0].message.content