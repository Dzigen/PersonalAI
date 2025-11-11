import torch
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = 'ai-forever/FRIDA'
SAVE_DIR = f'../../models/{MODEL_NAME}'

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)
