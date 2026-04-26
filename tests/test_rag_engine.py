"""
tests/test_rag_engine.py — Unit tests for the RAG retrieval engine
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine import retrieve_context, load_knowledge_base, _tokenize

SAMPLE_DOCS = [
    {"id": "genre_pop", "type": "genre", "key": "pop",
     "content": "Pop music is characterized by catchy melodies and mainstream appeal. High danceability and energy."},
    {"id": "genre_lofi", "type": "genre", "key": "lofi",
     "content": "Lo-fi hip hop features slow tempos, high acousticness, and chill relaxed moods for studying."},
    {"id": "mood_happy", "type": "mood", "key": "happy",
     "content": "Happy music features major keys, high valence, and energetic upbeat production."},
    {"id": "mood_chill", "type": "mood", "key": "chill",
     "content": "Chill music prioritizes relaxation, low energy, and ambient background sounds."},
]


def test_retrieve_returns_relevant_docs():
    results = retrieve_context("pop music catchy danceability", SAMPLE_DOCS, top_k=2)
    ids = [r["id"] for r in results]
    assert "genre_pop" in ids


def test_retrieve_lofi_query():
    results = retrieve_context("lofi chill studying acousticness slow", SAMPLE_DOCS, top_k=2)
    ids = [r["id"] for r in results]
    assert "genre_lofi" in ids


def test_retrieve_top_k_respected():
    results = retrieve_context("music mood energy", SAMPLE_DOCS, top_k=2)
    assert len(results) <= 2


def test_retrieve_returns_score_field():
    results = retrieve_context("pop happy", SAMPLE_DOCS, top_k=3)
    for r in results:
        assert "score" in r
        assert isinstance(r["score"], float)


def test_tokenize_lowercases():
    tokens = _tokenize("Pop Music ENERGY")
    assert "pop" in tokens
    assert "music" in tokens
    assert "energy" in tokens


def test_retrieve_empty_query_returns_nothing():
    results = retrieve_context("", SAMPLE_DOCS, top_k=3)
    assert results == []


def test_load_knowledge_base(tmp_path):
    import json
    kb = [{"id": "test", "type": "genre", "key": "test",
           "content": "Test content for loading."}]
    kb_file = tmp_path / "kb.json"
    kb_file.write_text(json.dumps(kb))
    docs = load_knowledge_base(str(kb_file))
    assert len(docs) == 1
    assert docs[0]["id"] == "test"