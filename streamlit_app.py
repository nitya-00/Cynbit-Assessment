"""Document Reader dashboard. Start the FastAPI API before this app."""
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("DOCUMENT_READER_API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Document Reader", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"] {background: #f8fafc; color: #111827;}
    .block-container {max-width: 1180px; padding-top: 2.5rem;}
    [data-testid="stSidebar"] {background: #ffffff; border-right: 1px solid #dbe3ef;}
    [data-testid="stSidebar"] * {color: #111827;}
    .hero {padding: 1.5rem 0 1.1rem;}
    .hero h1 {font-size: 2.5rem; margin: 0; color: #111827; font-weight: 700;}
    .hero p {font-size: 1.05rem; color: #334155; margin: .5rem 0 0;}
    .value-card {background: #ffffff; border: 1px solid #dbe3ef; border-radius: 12px; padding: 1rem; min-height: 105px; box-shadow: 0 1px 2px rgba(15,23,42,.05);}
    .value-card h4 {margin: 0 0 .4rem; color: #111827;}
    .value-card p {margin: 0; color: #475569; font-size: .92rem;}
    .stApp p, .stApp label, .stApp span, .stApp h2, .stApp h3 {color: #111827;}
    [data-testid="stMetricValue"] {color: #111827;}
    .stButton > button[kind="primary"] {background: #2563eb; color: #ffffff; border: 0;}
    .stButton > button[kind="primary"]:hover {background: #1d4ed8; color: #ffffff;}
</style>
""", unsafe_allow_html=True)

def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(method, f"{API_BASE_URL}{endpoint}", timeout=120, **kwargs)
        if response.ok:
            return response.json(), None
        return None, response.json().get("detail", response.text)
    except requests.RequestException as error:
        return None, f"Cannot reach backend at {API_BASE_URL}: {error}"

st.markdown("""
<div class="hero">
  <h1>Document Reader</h1>
  <p>Find the right part of a PDF quickly, with page-level evidence instead of a generic chat answer.</p>
</div>
""", unsafe_allow_html=True)
health, error = api_request("GET", "/health")
if error:
    st.error(error)
    st.caption("Start it with: `venv/bin/uvicorn app.main:app --reload --port 8000`")
    st.stop()
st.success("Backend connected")
card1, card2, card3 = st.columns(3)
card1.markdown('<div class="value-card"><h4>Meaning-based search</h4><p>Find related content even when the question uses different words.</p></div>', unsafe_allow_html=True)
card2.markdown('<div class="value-card"><h4>Page evidence</h4><p>Every result keeps the original PDF page and source filename.</p></div>', unsafe_allow_html=True)
card3.markdown('<div class="value-card"><h4>Local processing</h4><p>Embeddings and search run with local Ollama and FAISS tools.</p></div>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("Add a document")
    st.caption("Use text-based PDFs. Scanned PDFs need OCR support.")
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
    st.info("Upload a PDF to create a searchable document library."); st.stop()

labels = {f"{d['filename']} — {d['status']}": d["document_id"] for d in documents}
selected_label = st.selectbox("Document library", list(labels), index=0)
document_id = labels[selected_label]
selected = next(d for d in documents if d["document_id"] == document_id)
metric1, metric2, metric3 = st.columns(3)
metric1.metric("Selected document", selected["filename"])
metric2.metric("Status", selected["status"].title())
metric3.metric("Search mode", "Semantic retrieval")

if selected["status"] != "processed":
    if st.button("Process document", type="primary"):
        with st.spinner("Extracting, chunking, embedding, and indexing..."):
            data, error = api_request("POST", f"/api/documents/{document_id}/process")
        if error: st.error(error)
        else: st.success(f"Processed {data['document'].get('chunk_count', 0)} chunks"); st.rerun()
    st.stop()

tab_chat, tab_details = st.tabs(["Search document", "Document details"])
with tab_chat:
    st.caption("Ask a clear question. The result shows the matching source passages, so you can verify the answer yourself.")
    question = st.text_area("Your question", placeholder="Which database does the project use?", height=110)
    top_k = st.slider("Number of source passages", 1, 10, 5, help="More passages give more context but may include less relevant text.")
    if st.button("Search document", type="primary", disabled=not question.strip(), use_container_width=True):
        with st.spinner("Searching document..."):
            result, error = api_request("POST", "/api/chat", json={"document_id": document_id, "question": question, "top_k": top_k})
        if error: st.error(error)
        else:
            st.subheader("Retrieved result")
            st.write(result["answer"])
            if result.get("insufficient_information"): st.warning("The document may not contain enough information.")
            st.subheader("Source citations")
            for citation in result.get("citations", []):
                st.caption(f"{citation['source']} · Page {citation['page_number']} · {citation['chunk_id']}")
            with st.expander("Retrieved passages"):
                for chunk in result.get("retrieved_chunks", []): st.write(f"Page {chunk['page_number']}: {chunk['text']}")
with tab_details:
    st.json(selected)
