# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommender system.
Given a user's taste profile (favorite genre, mood, target energy level, and acoustic preference), the system scores every song in the catalog and returns the top-k matches with plain-language explanations.
The goal is to understand how real-world recommenders translate raw data into personalized suggestions — and where that process can go wrong.

---

## How The System Works

Each `Song` object stores ten attributes loaded from `songs.csv`: `id`, `title`, `artist`, `genre`, `mood`, `energy` (0–1), `tempo_bpm`, `valence` (positivity, 0–1), `danceability`, and `acousticness`.

A `UserProfile` captures four preference signals: `favorite_genre`, `favorite_mood`, `target_energy`, and a boolean `likes_acoustic`.

The `Recommender` computes a weighted score for every song using this **Algorithm Recipe**:

| Signal | Points | Rationale |
|---|---|---|
| Genre match | +2.5 | Strongest predictor of taste |
| Mood match | +1.5 | Drives the listening vibe |
| Energy proximity | 0–1.5 | `1.5 × (1 − |target − song|)` — rewards closeness |
| Acoustic match | +0.5 | Bonus when preference aligns with acousticness |
| Valence boost | 0–0.5 | Light positive-song preference |

Songs are ranked by total score (highest first) and the top-k are returned.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Mac / Linux
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### Run the CLI

```bash
python main.py
```

### Run Tests

```bash
pytest test_recommender.py -v
```

---

## Experiments You Tried

**Experiment 1 — Weight shift (genre 2.5 → 1.0):**
Lowering genre weight caused indie-pop and synthwave songs to compete with pop for the "Happy Pop Fan" profile. The genre signal dominates by design; weakening it creates more cross-genre variety but less precision.

**Experiment 2 — Remove mood check:**
Commenting out the mood bonus made the "Chill Lofi" profile occasionally surface ambient tracks with no chill label, purely on energy and acousticness. Mood is a meaningful tiebreaker.

**Experiment 3 — Edge case "High energy + sad mood":**
No song in the dataset has `mood=sad`, so the mood bonus never fires. The system still returns reasonable results (high-energy tracks) but the explanation never mentions a mood match — highlighting a data gap.

---

## Limitations and Risks

- The catalog has only 20 songs, so the rock profile always surfaces the same three rock tracks.
- Genre strings must match exactly (e.g. "indie pop" ≠ "pop") — a user who prefers "pop" will miss indie-pop songs.
- The system has no concept of lyric language, cultural context, or listening history.
- Energy and acousticness are the only continuous features; tempo and danceability are unused, leaving potential signal on the table.

See `model_card.md` for deeper bias analysis.

---

## Reflection

Building this recommender made it clear how much a "smart" system relies on the quality and diversity of its data. The scoring weights felt intuitive at first, but testing adversarial profiles (e.g., `energy=0.9, mood=sad`) quickly revealed gaps: the model happily recommends high-energy songs regardless of emotional tone because sadness is absent from the catalog. Real platforms like Spotify solve this with massive datasets and collaborative signals — but those systems inherit whatever biases exist in users' historical listening behavior. This small simulation makes that tradeoff viscerally obvious.

[**→ Full Model Card**](model_card.md)