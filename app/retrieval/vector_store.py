import json
from pathlib import Path
import faiss
from app.config import VECTOR_STORE_DIR
from app.embeddings.embedder import generate_document_embeddings, generate_query_embedding

def _path(document_id):
    path=VECTOR_STORE_DIR/document_id; path.mkdir(parents=True, exist_ok=True); return path
def build_vector_store(document_id, chunks):
    vectors=generate_document_embeddings([c["text"] for c in chunks]); faiss.normalize_L2(vectors)
    index=faiss.IndexFlatIP(vectors.shape[1]); index.add(vectors); path=_path(document_id)
    faiss.write_index(index, str(path/"index.faiss")); (path/"metadata.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    return index.ntotal
def load_vector_store(document_id):
    path=_path(document_id); index_file=path/"index.faiss"; metadata_file=path/"metadata.json"
    if not index_file.exists() or not metadata_file.exists(): raise FileNotFoundError("Document has not been processed.")
    return faiss.read_index(str(index_file)), json.loads(metadata_file.read_text(encoding="utf-8"))
def search_vector_store(document_id, query, top_k=5):
    index,chunks=load_vector_store(document_id); vector=generate_query_embedding(query)
    if vector.shape[1] != index.d: raise ValueError("Embedding dimension mismatch.")
    faiss.normalize_L2(vector); scores,positions=index.search(vector,min(top_k,index.ntotal))
    return [{**chunks[int(pos)], "similarity_score":float(score)} for score,pos in zip(scores[0],positions[0]) if pos>=0]
