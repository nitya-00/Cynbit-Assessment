from app.llm.rag_chain import rerank_chunks, validate_citation_ids

def test_reranking_prefers_question_terms():
    chunks = [
        {"chunk_id":"a","text":"PostgreSQL database","similarity_score":0.60},
        {"chunk_id":"b","text":"Attendance management","similarity_score":0.61},
    ]
    assert rerank_chunks("Which database uses PostgreSQL?", chunks, 1)[0]["chunk_id"] == "a"

def test_citations_are_valid_unique_and_cleared_when_insufficient():
    chunks = [{"chunk_id":"one"}, {"chunk_id":"two"}]
    assert validate_citation_ids(["one", "missing", "one", "two"], chunks, False) == ["one", "two"]
    assert validate_citation_ids(["one"], chunks, True) == []
