from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict
import gc
import torch

from src.agent_model import AgentModel


class RemoteAgentRequestBody(BaseModel):
    user_prompt: str
    system_prompt: str = Field(default=None)
    assistant_prompt: str = Field(default=None)
    gen_strategy: Dict = Field(default=None)

agent = AgentModel()

app = FastAPI()

@app.post("/generate")
async def generate(body: RemoteAgentRequestBody):
    output = agent.generate(
        user_prompt=body.user_prompt, 
        assistant_prompt=body.assistant_prompt, 
        gen_strategy=body.gen_strategy,
        system_prompt=body.system_prompt

    )
    torch.cuda.empty_cache()
    gc.collect()
    
    return {'generated_output': output}

@app.get("/")
async def info():
    return "Hello from remote Agent-model!"