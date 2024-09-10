from fastapi import FastAPI
from .agent_model import AgentModel
from pydantic import BaseModel
from typing import Dict

class RemoteAgentRequestBody(BaseModel):
    user_prompt: str
    assistant_prompt: str
    gen_strategy: Dict

app = FastAPI()
agent = AgentModel()

@app.post("/generate")
async def generate(body: RemoteAgentRequestBody):
    output = agent.generate(
        user_prompt=body.user_prompt, 
        assistant_prompt=body.assistant_prompt, 
        gen_strategy=body.gen_strategy
    )
    return {'generated_output': output}

@app.head("/")
async def info():
    return "Hello from remote Agent-model!"