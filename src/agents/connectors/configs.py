import torch

from ..utils import AgentConnectorConfig

GIGACHAT_KEY = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='
DEFAULT_GIGACHAT_CONFIG = AgentConnectorConfig(
    gen_strategy={'top_k': 1, 'top_p': 0, 'temperature': 0},
    credentials={'token': GIGACHAT_KEY,
                 'scope': 'GIGACHAT_API_CORP', 'model': "GigaChat-Pro"},
    ext_params={'timeout': 560, 'trials': 5, 'verify_ssl_certs': False})

DEFAULT_LOCALAGENT_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_new_tokens': 2048,
                  'seed': 42, 'top_k': 1, 'temperature': 0.0},
    credentials={'model_name_or_path': '../models/Undi95/Meta-Llama-3-8B-Instruct-hf',
                 'torch_dtype': torch.bfloat16},
    ext_params={'num_workers': 4})

DEFAULT_OLLAMA_CONFIG = AgentConnectorConfig(
    gen_strategy={'num_predict': 2048, 'seed': 42,
                  'top_k': 1, 'temperature': 0.0},
    credentials={'model': 'llama3.2'},
    ext_params={'host': 'localhost', 'port': 11434, 'timeout': 560, 'keep_alive': -1})

DEEPSEEK_KEY = 'sk-aa2371fe6326458bbd63bf91dcb6a4a4'
DEEPSEEK_CONFIG = AgentConnectorConfig(
    gen_strategy={'seed': 42, 'top_p': 10e-16, 'temperature': 0.0,
                  'frequency_penalty': 0, 'presence_penalty': 0},
    credentials={'token': DEEPSEEK_KEY, 'model': 'deepseek-chat',
                 'base_url': 'https://api.deepseek.com'},
    ext_params={'timeout': 560, 'max_retries': 5})

GPT4OMINI_KEY = "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"
GPT4OMINI_CONFIG = AgentConnectorConfig(
    gen_strategy={'seed': 42, 'top_p': 10e-16, 'temperature': 0.0,
                  'frequency_penalty': 0, 'presence_penalty': 0},
    credentials={'token': GPT4OMINI_KEY,
                 'model': 'gpt-4o-mini', 'base_url': None},
    ext_params={'timeout': 560, 'max_retries': 5})

DEFAULT_STUBAGENT_CONFIG = AgentConnectorConfig()
