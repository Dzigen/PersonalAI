from ..utils import SYSTEM_PROMPT

import os
from typing import Dict
from gigachat import GigaChat 
from gigachat.models import Chat, Messages 
from gigachat.exceptions import GigaChatException
from httpx import TimeoutException, Timeout
import time
import gc

# https://github.com/VRSEN/agency-swarm/issues/99
# https://github.com/ai-forever/gigachat/blob/main/src/gigachat/client.py#L182

GIGACHAT_CREDS = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='

class GigaChatAgent:
    def __init__(self, creds: str = GIGACHAT_CREDS, scope: str = 'GIGACHAT_API_CORP', model: str = "GigaChat-Pro",
                 verify_ssl_certs: bool = False, timeout_sleep_time: int =480) -> None:
        self.giga_model = GigaChat(
            credentials=creds, scope=scope, verify_ssl_certs=verify_ssl_certs, model=model, timeout=timeout_sleep_time)
        self.creds = creds
        self.scope = scope 
        self.model = model
        self.verify_ssl_certs = verify_ssl_certs
        self.timeout_sleep = timeout_sleep_time
        
    def generate(self, user_prompt: str, assistant_prompt: str = None, 
                 system_prompt: str = None, gen_strategy: Dict = {'temperature': 0.001}) -> str:
        chat = Chat(messages=[Messages(role='system', content=system_prompt if system_prompt is not None else SYSTEM_PROMPT), 
                            Messages(role='user', content=user_prompt)], **gen_strategy) 
        #success_flag = False
        #while not success_flag:
            #try:
        response = self.giga_model.chat(chat) 
            #    success_flag = True
            #except TimeoutException as e:
            #    print(f"gigachat error: {str(e)}")
            #    print("Waiting timeout-block...")
            #    self.giga_model.close()
            #    self.giga_model.aclose()
            #    del self.giga_model
            #    time.sleep(self.timeout_sleep)
            #    print("response generation restart")
            #    self.giga_model = GigaChat(
            #        credentials=self.creds, scope=self.scope, 
            #        verify_ssl_certs=self.verify_ssl_certs, model=self.model) 
            #    gc.collect()
        return response.choices[0].message.content