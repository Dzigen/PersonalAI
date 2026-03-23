from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BAAI/bge-m3'
SAVE_DIR = f'../../models/{MODEL_NAME}'

embedder= SentenceTransformer(MODEL_NAME)
embedder.save_pretrained(SAVE_DIR)