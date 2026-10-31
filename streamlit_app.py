"""Document Reader dashboard. Start the FastAPI API before this app."""
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("DOCUMENT_READER_API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Document Reader", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background: #ffffff !important; color: #111827 !important;}
    .block-container {max-width: 1180px; padding-top: 2.5rem;}
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {background: #ffffff !important; border-right: 1px solid #dbe3ef;}
    [data-testid="stSidebar"] * {color: #111827;}
    .hero {padding: 1.5rem 0 1.1rem;}
    .hero h1 {font-size: 2.5rem; margin: 0; color: #111827; font-weight: 700;}
    .hero p {font-size: 1.05rem; color: #334155; margin: .5rem 0 0;}
    .value-card {background: #ffffff; border: 1px solid #dbe3ef; border-radius: 12px; padding: .75rem; min-height: 82px; box-shadow: 0 1px 2px rgba(15,23,42,.05);}
    .value-card h4 {margin: 0 0 .4rem; color: #111827;}
    .value-card p {margin: 0; color: #475569; font-size: .92rem;}
    .stApp p, .stApp label, .stApp span, .stApp h2, .stApp h3 {color: #111827;}
    [data-testid="stMetricValue"] {color: #111827;}
    .stButton > button[kind="primary"] {background: #2563eb; color: #ffffff; border: 0;}
    .stButton > button[kind="primary"]:hover {background: #1d4ed8; color: #ffffff;}
    [data-testid="stFileUploader"] {background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: .5rem;}
    [data-testid="stFileUploaderDropzone"], [data-testid="stFileUploaderDropzone"] * {background: #ffffff !important; color: #111827 !important; border-color: #cbd5e1 !important;}
    [data-baseweb="select"] > div {background: #ffffff !important; color: #111827 !important; border-color: #cbd5e1 !important;}
    [data-baseweb="select"], [data-baseweb="select"] *, [data-baseweb="select"] div {background-color: #ffffff !important; color: #111827 !important;}
    [data-baseweb="select"] span, [data-baseweb="select"] input {color: #111827 !important; -webkit-text-fill-color: #111827 !important;}
    [data-baseweb="menu"] {background: #ffffff !important;}
    [data-baseweb="menu"] * {color: #111827 !important;}
    textarea, input, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {background: #ffffff !important; color: #111827 !important; -webkit-text-fill-color: #111827 !important;}
    [data-testid="stTabs"] button, [data-testid="stTabs"] [role="tablist"], [data-testid="stExpander"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary {background: #ffffff !important; color: #111827 !important;}
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {color: #111827;}
    .pipeline {background: #ffffff; border: 1px solid #dbe3ef; border-radius: 12px; padding: 1rem 1.2rem; margin: .8rem 0 1.2rem; color: #111827;}
    .pipeline-step {font-weight: 600; color: #1e3a8a; margin: .15rem 0;}
    .pipeline-arrow {color: #64748b; margin-left: .55rem;}
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

header, add_document = st.columns([3, 1])
with header:
    st.markdown("""
<div class="hero">
  <h1>Document Reader</h1>
  <p>Find the right part of a PDF quickly, with page-level evidence instead of a generic chat answer.</p>
</div>
""", unsafe_allow_html=True)
    card1, card2, card3 = st.columns(3)
    card1.markdown('<div class="value-card"><h4>Meaning search</h4><p>Search by meaning.</p></div>', unsafe_allow_html=True)
    card2.markdown('<div class="value-card"><h4>Page evidence</h4><p>See the source page.</p></div>', unsafe_allow_html=True)
    card3.markdown('<div class="value-card"><h4>Local AI</h4><p>Ollama and FAISS.</p></div>', unsafe_allow_html=True)
with add_document:
    st.markdown("### Add document")
    file = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")
    upload_clicked = st.button("Upload and prepare", type="primary", use_container_width=True)
    st.markdown("""
    <div class="pipeline">
      <div class="pipeline-step">Reading PDF</div><div class="pipeline-arrow">↓</div>
      <div class="pipeline-step">Creating embeddings</div><div class="pipeline-arrow">↓</div>
      <div class="pipeline-step">Saving FAISS index</div><div class="pipeline-arrow">↓</div>
      <div class="pipeline-step">Ready for search</div>
    </div>
    """, unsafe_allow_html=True)
health, error = api_request("GET", "/health")
if error:
    st.error(error)
    st.caption("Start it with: `venv/bin/uvicorn app.main:app --reload --port 8000`")
    st.stop()
st.success("Backend connected")

if upload_clicked:
    if not file:
        st.warning("Choose a PDF first.")
    else:
        with st.spinner("Preparing your document..."):
            data, error = api_request("POST", "/api/documents/upload", files={"file": (file.name, file.getvalue(), "application/pdf")})
        if error: st.error(error)
        else:
            st.session_state["selected_document"] = data["document"]["document_id"]
            st.session_state["pipeline_complete"] = True
            st.success("Document is ready to search.")

documents, error = api_request("GET", "/api/documents")
if error:
    st.error(error); st.stop()
documents = documents or []
if not documents:
    st.info("Choose a PDF. Uploading automatically prepares it for search."); st.stop()

labels = {f"{d['filename']} — {d['status']}": d["document_id"] for d in documents}
options = list(labels)
selected_id = st.session_state.get("selected_document")
selected_index = next((index for index, label in enumerate(options) if labels[label] == selected_id), 0)
selected_label = st.selectbox("Document library", options, index=selected_index)
document_id = labels[selected_label]
selected = next(d for d in documents if d["document_id"] == document_id)
st.caption(f"Ready to search: {selected['filename']} · {selected.get('chunk_count', 0)} chunks")

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
            st.session_state["last_result"] = result
            st.subheader("Answer")
            st.write(result["answer"])
            if result.get("insufficient_information"): st.warning("The document may not contain enough information.")
            st.subheader("Source citations")
            for citation in result.get("citations", []):
                st.caption(f"{citation['source']} · Page {citation['page_number']} · {citation['chunk_id']}")
            with st.expander("Retrieved passages"):
                for chunk in result.get("retrieved_chunks", []): st.write(f"Page {chunk['page_number']}: {chunk['text']}")
    evidence_clicked = st.button("No hallucination check: document-only evidence", use_container_width=True, disabled="last_result" not in st.session_state)
    if evidence_clicked:
            evidence = st.session_state["last_result"]
            chunks = evidence.get("retrieved_chunks", [])
            confidence = max((chunk.get("rerank_score", chunk.get("similarity_score", 0)) for chunk in chunks), default=0)
            if evidence.get("insufficient_information"):
                st.warning("Evidence check: the system did not find enough document evidence, so it should not make a factual answer.")
            else:
                st.success(f"Evidence check: {len(evidence.get('citations', []))} citation(s) and {len(chunks)} retrieved passage(s). Retrieval strength: {min(round(confidence * 100), 100)}%.")
                st.caption("This is evidence strength from the uploaded PDF, not a guaranteed hallucination prediction. No external data is used.")
with tab_details:
    st.subheader("Document details")
    st.table({"Item": ["Filename", "Status", "Pages", "Chunks"], "Value": [selected.get("filename", ""), selected.get("status", ""), selected.get("page_count", "-"), selected.get("chunk_count", "-")]})
    st.caption("The no-hallucination evidence check becomes available after you search this document.")
