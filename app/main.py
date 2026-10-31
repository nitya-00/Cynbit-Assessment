from fastapi import FastAPI, UploadFile, File, HTTPException
from app.schemas.document import ChatRequest
from app.services.document_service import upload_document, process_document
from app.services.document_registry import get_document, list_documents
from app.llm.rag_chain import answer_document_question

app=FastAPI(title="Document Reader",version="1.0.0")
def public(doc): return {k:v for k,v in doc.items() if k not in {"file_path","error"}}
@app.get("/")
def root(): return {"message":"Welcome to Document Reader","status":"running"}
@app.get("/health")
def health(): return {"status":"healthy"}
@app.post("/api/documents/upload")
async def upload(file:UploadFile=File(...)):
    try:
        document = upload_document(await file.read(), file.filename or "")
        document = process_document(document["document_id"])
        return {"message":"Document uploaded and processed successfully.","document":public(document)}
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
        return answer_document_question(request.document_id,request.question,request.top_k)
    except FileNotFoundError: raise HTTPException(409,"Document has not been processed.")
