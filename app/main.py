from fastapi import FastAPI, UploadFile, File, HTTPException
from app.schemas.document import ChatRequest
from app.services.document_service import upload_document, process_document
from app.services.document_registry import get_document, list_documents
from app.retrieval.vector_store import search_vector_store

app=FastAPI(title="Local Document Reader",version="1.0.0")
def public(doc): return {k:v for k,v in doc.items() if k not in {"file_path","error"}}
@app.get("/")
def root(): return {"message":"Welcome to Local Document Reader","status":"running"}
@app.get("/health")
def health(): return {"status":"healthy"}
@app.post("/api/documents/upload")
async def upload(file:UploadFile=File(...)):
    try: return {"message":"Document uploaded successfully.","document":public(upload_document(await file.read(),file.filename or ""))}
    except ValueError as e: raise HTTPException(400,str(e))
@app.get("/api/documents")
def documents(): return [public(d) for d in list_documents()]
@app.post("/api/documents/{document_id}/process")
def process(document_id:str):
    try: return {"message":"Document processed successfully.","document":public(process_document(document_id))}
    except KeyError: raise HTTPException(404,"Document not found.")
    except Exception as e: raise HTTPException(400,str(e))
@app.post("/api/chat")
def chat(request:ChatRequest):
    try:
        results=search_vector_store(request.document_id,request.question,request.top_k)
        return {"answer":"Generation model integration is available in Notebook 03; retrieved evidence returned below.","insufficient_information":not bool(results),"citations":[{"chunk_id":x["chunk_id"],"source":x["source"],"page_number":x["page_number"]} for x in results],"retrieved_chunks":results}
    except FileNotFoundError: raise HTTPException(409,"Document has not been processed.")
