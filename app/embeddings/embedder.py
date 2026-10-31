import numpy as np
import ollama
from app.config import OLLAMA_HOST, EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE

client = ollama.Client(host=OLLAMA_HOST)
def _embed(texts, prefix):
    if not texts: raise ValueError("No texts provided.")
    values=[]
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        result=client.embed(model=EMBEDDING_MODEL, input=[prefix + text for text in texts[start:start+EMBEDDING_BATCH_SIZE]])
        values.extend(result.embeddings)
    return np.ascontiguousarray(values, dtype=np.float32)
def generate_document_embeddings(texts): return _embed(texts, "search_document: ")
def generate_query_embedding(query): return _embed([query.strip()], "search_query: ")
