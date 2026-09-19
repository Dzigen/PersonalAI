import torch
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = 'intfloat/multilingual-e5-base'
SAVE_DIR = f'../../models/{MODEL_NAME}'

TOKEN= ... # TO CHANGE

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=TOKEN)
model = AutoModel.from_pretrained(MODEL_NAME, token=TOKEN)

model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)
