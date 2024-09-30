import transformers
import torch
import requests
from time import sleep

from .parent_agent import GPTagent

VPS_IP = "10.5.1.1"
port = 8000

class LLaMAagent(GPTagent):
    def __init__(self, pipeline = None):
        super().__init__("", "", "")
        self.pipeline = transformers.pipeline(
            "text-generation",
            model="Undi95/Meta-Llama-3-8B-Instruct-hf",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        ) if pipeline is None else pipeline
        
    def generate(self, messages, jsn = False, t = 0.2):
        prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
        )

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        
        outputs = self.pipeline(
            prompt,
            max_new_tokens=2048,
            eos_token_id=terminators,
            do_sample=True,
            temperature=t,
            top_p=0.9,
        )
        
        return outputs[0]["generated_text"][len(prompt):]
    

class LLaMAagentLocal:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def generate(self, prompt):
        URL = "https://b451-178-176-73-130.ngrok-free.app/llama" 
        prompt = prompt + "&&&&&" + self.system_prompt
        response = requests.post( 
            URL, params = {"prompt": prompt}
        )
        return response.json()["response"]


        