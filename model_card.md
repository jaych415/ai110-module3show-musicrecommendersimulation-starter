# Model Card — RAG-Enhanced Music Recommender

## System Overview

**Base model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`) via Anthropic API  
**Retrieval method:** Keyword overlap (Jaccard similarity) over a curated JSON knowledge base  
**Task:** Generate grounded, human-readable explanations for content-based music recommendations  
**Input:** User preference profile + top-ranked song + retrieved prose context  
**Output:** 2-3 sentence natural language explanation with confidence score  

---

## Intended Use

- Educational demonstration of RAG-enhanced recommendation systems
- Portfolio artifact showing AI system integration skills
- Music discovery assistant for users who want to understand *why* a song was recommended

---

## Limitations and Biases

**Dataset bias:** The 25-song dataset skews heavily toward Western English-language music — pop, rock, and lofi hip hop. Non-Western genres (K-pop aside from BTS, Latin, Afrobeats, classical, jazz) are absent. A real deployment would need a far more diverse dataset.

**Knowledge base bias:** The 13 prose documents were written manually and reflect the author's understanding of these genres and artists. Descriptions may not match how listeners from other cultural backgrounds experience this music.

**Genre taxonomy:** The system uses only three genre labels (pop, lofi, rock). Real music exists on a continuous spectrum. A song like "Bohemian Rhapsody" gets tagged "rock" even though it blends opera, ballad, and hard rock.

**Retrieval brittleness:** Jaccard keyword overlap fails when the user query uses different vocabulary than the knowledge base. A query for "indie" won't match documents that say "singer-songwriter."

**LLM hallucination risk:** Claude generates explanations from retrieved context, but could still produce inaccurate statements about artists or genres, especially for less-documented acts.

---

## Potential Misuse

The recommendation system itself is low-risk. However:

- A bad actor could construct a knowledge base with biased or false artist descriptions to steer users toward or away from certain music for non-musical reasons (e.g. promoting a label's artists).
- The confidence scoring could create false trust — a high confidence score reflects retrieval quality, not factual accuracy of the explanation.

**Mitigations:** Keep the knowledge base human-curated and version-controlled. Add source citations to knowledge base documents. Cap explanation generation with a system prompt that discourages confident claims without evidence.

---

## Testing Results

| Test type | Cases | Passed | Notes |
|---|---|---|---|
| Unit tests (pytest) | 14 | 14 | No API access required |
| Test harness | 10 | 10 | Local retrieval + recommender only |
| Manual review | 9 | 9/9 explanations judged accurate |  |

Confidence scores averaged **0.70** across 9 RAG explanations during manual testing. All explanations correctly identified the primary reason for the recommendation (genre/mood/energy match). One explanation slightly overstated an artist's chart performance — an example of LLM hallucination risk noted above.

---

## AI Collaboration During This Project

### Helpful suggestion
When designing the RAG retriever, Claude suggested using a Jaccard-style token overlap score rather than cosine similarity over TF-IDF vectors. This was helpful because it kept the system dependency-free (no `scikit-learn` or `numpy` needed) while still producing accurate retrieval for the structured queries this system generates. The suggestion matched the constraint of the original project, which also had no external dependencies.

### Flawed suggestion
Claude initially suggested wrapping the entire `rag_main.py` pipeline in a `while True:` interactive loop so users could enter custom profiles at the command line. This sounded useful in theory, but in practice it would have made the system harder to test automatically (the test harness runs non-interactively) and would have complicated the Loom demo recording. The profile-based CLI with `--profile` and `--top` flags was a better design for the actual use cases.

---

## Reflection

This project demonstrated that even a simple retrieval mechanism — keyword overlap over a small curated knowledge base — can meaningfully improve the quality of AI-generated explanations when the retrieval queries are structured. The biggest insight was the value of separating *scoring* (deterministic, fast, no API) from *explanation* (probabilistic, slower, API-dependent). This separation makes the system more testable, more reliable, and more cost-efficient than a pure LLM approach.

As an AI engineer, this project shows I can integrate an LLM into a larger system responsibly: with fallback handling, logging, confidence scoring, and automated tests that don't require mocking the API.