"""
rag_main.py — RAG-Enhanced Music Recommender CLI

Extends the original Module 3 recommender with Retrieval-Augmented Generation:
  1. Loads songs from data/songs.csv (same as before)
  2. Scores and ranks songs using the original content-based algorithm
  3. For each top recommendation, retrieves relevant genre/artist/mood context
     from data/knowledge_base.json
  4. Passes retrieved context + song info to Claude API for a grounded explanation

Run with:
    python rag_main.py
    python rag_main.py --profile "Happy Pop Fan"
    python rag_main.py --top 3
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.recommender import load_songs, score_song, recommend_songs
from src.rag_engine import RAGExplainer

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler("logs/rag_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------
PROFILES = {
    "Happy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "likes_acoustic": False,
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
    },
    "Intense Rock Head": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def run_profile(profile_name: str, prefs: dict, songs: list,
                explainer: RAGExplainer, top_k: int = 3) -> list:
    """Score, rank, RAG-explain, and print results for one profile."""
    print_header(f"Profile: {profile_name}")
    ranked = recommend_songs(prefs, songs, k=top_k)
    results = []

    for i, (song, base_score, base_explanation) in enumerate(ranked, start=1):
        print(f"\n  #{i}  {song['title']} — {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | "
              f"Energy: {song['energy']}")
        print(f"       Base Score: {base_score:.2f}")

        # RAG-enhanced explanation
        base_reasons = [r.strip() for r in base_explanation.split(";")]
        rag_explanation, retrieved_docs, confidence = explainer.explain(
            prefs, song, base_score, base_reasons
        )

        print(f"       Confidence: {confidence:.2f}")
        print(f"\n       💬 Why this song:")
        print(f"       {rag_explanation}")
        print(f"\n       📚 Retrieved context docs: "
              f"{[d['id'] for d in retrieved_docs]}")

        results.append({
            "rank": i,
            "song": song["title"],
            "artist": song["artist"],
            "base_score": base_score,
            "rag_confidence": confidence,
            "rag_explanation": rag_explanation,
            "retrieved_docs": [d["id"] for d in retrieved_docs]
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="RAG-Enhanced Music Recommender")
    parser.add_argument("--profile", type=str, default=None,
                        help="Run a single profile by name")
    parser.add_argument("--top", type=int, default=3,
                        help="Number of recommendations per profile (default: 3)")
    args = parser.parse_args()

    logger.info("Starting RAG-Enhanced Music Recommender")

    songs = load_songs("data/songs.csv")
    explainer = RAGExplainer(kb_path="data/knowledge_base.json", top_k=3)

    profiles_to_run = (
        {args.profile: PROFILES[args.profile]}
        if args.profile and args.profile in PROFILES
        else PROFILES
    )

    all_results = {}
    for profile_name, prefs in profiles_to_run.items():
        try:
            results = run_profile(profile_name, prefs, songs, explainer, top_k=args.top)
            all_results[profile_name] = results
        except Exception as e:
            logger.error(f"Failed on profile '{profile_name}': {e}")

    print(f"\n{'='*60}")
    stats = explainer.stats()
    print(f"  Session Stats: {stats['total_explanations']} explanations generated | "
      f"avg latency {stats['avg_latency_sec']:.2f}s")
    print(f"{'='*60}\n")

    # Save results log
    output_path = Path("logs") / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()