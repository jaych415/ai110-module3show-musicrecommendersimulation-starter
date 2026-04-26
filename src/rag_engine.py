"""
rag_engine.py — Retrieval-Augmented Generation engine for the music recommender.

Flow:
  1. Load prose documents from knowledge_base.json (genre/mood/artist context).
  2. Given a user query (genre + mood + artist), retrieve the top-k relevant docs
     using Jaccard keyword overlap — no external libraries required.
  3. Extract key sentences from retrieved docs and combine with song metadata
     to generate a grounded, context-aware explanation locally (no API needed).
"""

import json
import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def load_knowledge_base(kb_path: str) -> List[Dict]:
    with open(kb_path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    logger.info(f"Loaded {len(docs)} documents from knowledge base.")
    return docs


def _tokenize(text: str) -> set:
    return set(re.findall(r'\b\w+\b', text.lower()))


def retrieve_context(query: str, docs: List[Dict], top_k: int = 3) -> List[Dict]:
    """
    Retrieve top_k most relevant knowledge base docs for a query string.
    Uses token overlap (Jaccard similarity) — zero external dependencies.
    Returns list of dicts with 'id', 'content', 'score'.
    """
    query_tokens = _tokenize(query)
    scored = []
    for doc in docs:
        doc_tokens = _tokenize(doc["content"])
        if not doc_tokens:
            continue
        overlap = len(query_tokens & doc_tokens)
        score = overlap / (len(query_tokens | doc_tokens) + 1e-9)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [{"id": d["id"], "content": d["content"], "score": round(s, 4)}
               for s, d in scored[:top_k] if s > 0]
    logger.info(f"Retrieved {len(results)} docs for query: '{query[:60]}'")
    return results


def _extract_key_sentence(content: str, keywords: List[str]) -> str:
    """Pick the sentence from a doc that contains the most query keywords."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if len(s.strip()) > 20]
    if not sentences:
        return content[:120]
    kw_set = set(k.lower() for k in keywords)
    best = max(sentences, key=lambda s: len(_tokenize(s) & kw_set))
    return best if len(best) <= 140 else best[:137] + "..."


def _build_explanation(user_prefs: Dict, song: Dict, base_reasons: List[str],
                       retrieved: List[Dict]) -> str:
    """
    Compose a 2-3 sentence explanation grounded in retrieved knowledge base docs.
    No API call — pure local text assembly using extracted doc sentences.
    """
    genre = song.get("genre", "")
    mood = song.get("mood", "")
    artist = song.get("artist", "")
    title = song.get("title", "")
    energy = float(song.get("energy", 0.5))
    acousticness = float(song.get("acousticness", 0.5))

    keywords = [genre, mood, artist] + genre.split() + mood.split()

    match_parts = []
    if any("genre match" in r for r in base_reasons):
        match_parts.append(f"it matches your preferred {genre} genre")
    if any("mood match" in r for r in base_reasons):
        match_parts.append(f"fits your {mood} mood")
    if any("energy proximity" in r for r in base_reasons):
        energy_desc = "high" if energy > 0.7 else "low" if energy < 0.45 else "moderate"
        match_parts.append(f"has {energy_desc} energy ({energy}) close to your target")
    if any("acoustic" in r for r in base_reasons):
        if acousticness > 0.6:
            match_parts.append("has the organic acoustic texture you prefer")
        else:
            match_parts.append("has the clean non-acoustic production you prefer")

    sentence1 = f'"{title}" by {artist} was recommended because ' + ", and ".join(match_parts[:3]) + "."

    sentence2 = ""
    if retrieved:
        sentence2 = _extract_key_sentence(retrieved[0]["content"], keywords)

    sentence3 = ""
    if len(retrieved) > 1:
        s = _extract_key_sentence(retrieved[1]["content"], keywords)
        if s != sentence2:
            sentence3 = s

    parts = [s for s in [sentence1, sentence2, sentence3] if s]
    return " ".join(parts[:3])


class RAGExplainer:
    """
    Local RAG explainer: retrieves relevant knowledge base docs and generates
    grounded explanations without any external API calls.
    """

    def __init__(self, kb_path: str, top_k: int = 3):
        self.docs = load_knowledge_base(kb_path)
        self.top_k = top_k
        self._explain_count = 0

    def _build_query(self, user_prefs: Dict, song: Dict) -> str:
        return (
            f"genre:{song.get('genre','')} "
            f"mood:{song.get('mood','')} "
            f"artist:{song.get('artist','')} "
            f"energy:{song.get('energy','')} "
            f"acousticness:{song.get('acousticness','')} "
            f"user wants genre:{user_prefs.get('genre','')} "
            f"mood:{user_prefs.get('mood','')} "
            f"energy:{user_prefs.get('energy','')}"
        )

    def explain(self, user_prefs: Dict, song: Dict, base_score: float,
                base_reasons: List[str]) -> Tuple[str, List[Dict], float]:
        """
        Generate a RAG-grounded explanation locally.

        Returns (explanation_text, retrieved_docs, confidence_score)
        """
        query = self._build_query(user_prefs, song)
        retrieved = retrieve_context(query, self.docs, top_k=self.top_k)
        explanation = _build_explanation(user_prefs, song, base_reasons, retrieved)
        confidence = min(1.0, round(
            sum(d["score"] for d in retrieved) / max(1, len(retrieved)) * 10, 2
        )) if retrieved else 0.0
        self._explain_count += 1
        logger.info(f"RAG explain #{self._explain_count} | confidence={confidence:.2f}")
        return explanation, retrieved, confidence

    def stats(self) -> Dict:
        return {"total_explanations": self._explain_count, "avg_latency_sec": 0.0}