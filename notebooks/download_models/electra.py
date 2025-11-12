from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "google/electra-base-discriminator"
MODEL_SAVE_PATH = f'../../models/{MODEL_NAME}'

model = AutoModel.from_pretrained(MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model.save_pretrained(MODEL_SAVE_PATH)
tokenizer.save_pretrained(MODEL_SAVE_PATH)