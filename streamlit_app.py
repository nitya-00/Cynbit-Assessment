"""Local Document Reader dashboard. Start the FastAPI API before this app."""
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("DOCUMENT_READER_API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Local Document Reader", page_icon="📚", layout="wide")

def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(method, f"{API_BASE_URL}{endpoint}", timeout=120, **kwargs)
        if response.ok:
            return response.json(), None
        return None, response.json().get("detail", response.text)
    except requests.RequestException as error:
        return None, f"Cannot reach backend at {API_BASE_URL}: {error}"

st.title("📚 Local Document Reader")
health, error = api_request("GET", "/health")
if error:
    st.error(error)
    st.caption("Start it with: `venv/bin/uvicorn app.main:app --reload --port 8000`")
    st.stop()
st.success("Backend connected")

with st.sidebar:
    st.header("Upload PDF")
    file = st.file_uploader("Choose a PDF", type=["pdf"])
    if file and st.button("Upload document", use_container_width=True):
        data, error = api_request("POST", "/api/documents/upload", files={"file": (file.name, file.getvalue(), "application/pdf")})
        if error: st.error(error)
        else:
            st.success("Uploaded successfully")
            st.session_state["selected_document"] = data["document"]["document_id"]
            st.rerun()

documents, error = api_request("GET", "/api/documents")
if error:
    st.error(error); st.stop()
documents = documents or []
if not documents:
    st.info("Upload a PDF to begin."); st.stop()

labels = {f"{d['filename']} — {d['status']}": d["document_id"] for d in documents}
selected_label = st.selectbox("Document library", list(labels), index=0)
document_id = labels[selected_label]
selected = next(d for d in documents if d["document_id"] == document_id)
st.caption(f"Status: **{selected['status']}**")

if selected["status"] != "processed":
    if st.button("Process document", type="primary"):
        with st.spinner("Extracting, chunking, embedding, and indexing..."):
            data, error = api_request("POST", f"/api/documents/{document_id}/process")
        if error: st.error(error)
        else: st.success(f"Processed {data['document'].get('chunk_count', 0)} chunks"); st.rerun()
    st.stop()

tab_chat, tab_details = st.tabs(["Ask document", "Document details"])
with tab_chat:
    question = st.text_area("Question", placeholder="Which database does the project use?")
    top_k = st.slider("Retrieved passages", 1, 10, 5)
    if st.button("Ask", type="primary", disabled=not question.strip()):
        with st.spinner("Searching document..."):
            result, error = api_request("POST", "/api/chat", json={"document_id": document_id, "question": question, "top_k": top_k})
        if error: st.error(error)
        else:
            st.subheader("Answer")
            st.write(result["answer"])
            if result.get("insufficient_information"): st.warning("The document may not contain enough information.")
            st.subheader("Retrieved citations")
            for citation in result.get("citations", []):
                st.caption(f"{citation['source']} · Page {citation['page_number']} · {citation['chunk_id']}")
            with st.expander("Retrieved passages"):
                for chunk in result.get("retrieved_chunks", []): st.write(f"Page {chunk['page_number']}: {chunk['text']}")
with tab_details:
    st.json(selected)
