"""
test_harness.py — Automated Evaluation Script (Stretch Feature)

Runs the RAG-enhanced recommender on a set of predefined inputs and prints
a summary report: pass/fail per test case, confidence scores, and overall accuracy.

Run with:
    python test_harness.py
"""

import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import load_songs, recommend_songs, score_song
from src.rag_engine import RAGExplainer, retrieve_context, load_knowledge_base

logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "name": "Pop fan gets pop songs",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.80, "likes_acoustic": False},
        "expect_top_genre": "pop",
        "expect_min_score": 4.0,
    },
    {
        "name": "Lofi listener gets lofi songs",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
        "expect_top_genre": "lofi",
        "expect_min_score": 4.0,
    },
    {
        "name": "Rock fan gets rock songs",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
        "expect_top_genre": "rock",
        "expect_min_score": 4.0,
    },
    {
        "name": "High energy preference filters correctly",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
        "expect_top_genre": "rock",
        "expect_min_score": 3.5,
    },
    {
        "name": "Low energy preference filters correctly",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.25, "likes_acoustic": True},
        "expect_top_genre": "lofi",
        "expect_min_score": 3.0,
    },
    {
        "name": "Score is deterministic (same input = same output)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.75, "likes_acoustic": False},
        "expect_top_genre": "pop",
        "expect_min_score": 3.0,
        "check_determinism": True,
    },
    {
        "name": "RAG retrieval returns relevant docs for pop genre",
        "rag_query": "genre:pop mood:happy artist:Dua Lipa",
        "expect_doc_ids": ["genre_pop", "mood_happy"],
        "test_type": "rag_retrieval",
    },
    {
        "name": "RAG retrieval returns relevant docs for lofi genre",
        "rag_query": "genre:lofi mood:chill artist:Jinsang acousticness:0.9",
        "expect_doc_ids": ["genre_lofi", "mood_chill"],
        "test_type": "rag_retrieval",
    },
    {
        "name": "RAG retrieval returns relevant docs for rock genre",
        "rag_query": "genre:rock mood:intense artist:Metallica energy:0.95",
        "expect_doc_ids": ["genre_rock", "mood_intense"],
        "test_type": "rag_retrieval",
    },
    {
        "name": "Fallback: unknown genre still returns results",
        "prefs": {"genre": "jazz", "mood": "chill", "energy": 0.40, "likes_acoustic": True},
        "expect_top_genre": None,
        "expect_min_score": 0.0,
    },
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_recommender_test(case: Dict, songs: List[Dict]) -> Dict:
    prefs = case["prefs"]
    ranked = recommend_songs(prefs, songs, k=5)
    top_song, top_score, _ = ranked[0]

    passed = True
    notes = []

    if case.get("expect_top_genre") and top_song["genre"] != case["expect_top_genre"]:
        passed = False
        notes.append(f"Expected top genre '{case['expect_top_genre']}', got '{top_song['genre']}'")

    if top_score < case.get("expect_min_score", 0.0):
        passed = False
        notes.append(f"Score {top_score:.2f} below minimum {case['expect_min_score']}")

    if case.get("check_determinism"):
        ranked2 = recommend_songs(prefs, songs, k=5)
        if ranked[0][1] != ranked2[0][1]:
            passed = False
            notes.append("Non-deterministic: scores differ between runs")

    return {
        "passed": passed,
        "top_song": top_song["title"],
        "top_genre": top_song["genre"],
        "top_score": top_score,
        "notes": notes,
    }


def run_rag_test(case: Dict, docs: List[Dict]) -> Dict:
    query = case["rag_query"]
    results = retrieve_context(query, docs, top_k=3)
    retrieved_ids = [r["id"] for r in results]

    passed = True
    notes = []
    for expected_id in case.get("expect_doc_ids", []):
        if expected_id not in retrieved_ids:
            passed = False
            notes.append(f"Expected doc '{expected_id}' not in retrieved: {retrieved_ids}")

    return {
        "passed": passed,
        "retrieved_ids": retrieved_ids,
        "notes": notes,
    }


def main():
    print("\n" + "="*60)
    print("  🎵 Music Recommender — Automated Test Harness")
    print("="*60)

    songs = load_songs("data/songs.csv")
    docs = load_knowledge_base("data/knowledge_base.json")

    results = []
    passed_count = 0
    confidence_scores = []

    for i, case in enumerate(TEST_CASES, start=1):
        test_type = case.get("test_type", "recommender")
        print(f"\n[Test {i:02d}] {case['name']}")

        if test_type == "rag_retrieval":
            result = run_rag_test(case, docs)
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"         Status : {status}")
            print(f"         Docs   : {result['retrieved_ids']}")
        else:
            result = run_recommender_test(case, songs)
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"         Status : {status}")
            print(f"         Top    : {result['top_song']} ({result['top_genre']}) — score {result['top_score']:.2f}")

        if result["notes"]:
            for note in result["notes"]:
                print(f"         ⚠️  {note}")

        if result["passed"]:
            passed_count += 1

        results.append({"test": case["name"], **result})

    # Summary
    total = len(TEST_CASES)
    print(f"\n{'='*60}")
    print(f"  Results: {passed_count}/{total} passed")
    print(f"  Pass rate: {passed_count/total*100:.0f}%")
    print(f"{'='*60}\n")

    # Save JSON report
    report_path = Path("logs/harness_report.json")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"passed": passed_count, "total": total, "tests": results}, f, indent=2)
    print(f"  Report saved to {report_path}\n")


if __name__ == "__main__":
    main()