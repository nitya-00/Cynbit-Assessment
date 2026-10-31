import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "app" / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
VECTOR_STORE_DIR = STORAGE_DIR / "vector_store"
REGISTRY_PATH = STORAGE_DIR / "documents.json"
for directory in (UPLOAD_DIR, VECTOR_STORE_DIR): directory.mkdir(parents=True, exist_ok=True)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "llama2:latest")
CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_BATCH_SIZE, MAX_UPLOAD_SIZE = 1000, 150, 32, 20 * 1024 * 1024
