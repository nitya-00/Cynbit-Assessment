import json
from datetime import datetime, timezone
from app.config import REGISTRY_PATH
def load_registry(): return json.loads(REGISTRY_PATH.read_text()) if REGISTRY_PATH.exists() else {}
def save_registry(value): REGISTRY_PATH.write_text(json.dumps(value,indent=2),encoding="utf-8")
def get_document(document_id): return load_registry().get(document_id)
def list_documents(): return list(load_registry().values())
def update_document(document_id, **fields):
    registry=load_registry(); registry[document_id].update(fields,updated_at=datetime.now(timezone.utc).isoformat()); save_registry(registry); return registry[document_id]
