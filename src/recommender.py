"""
recommender.py — Music Recommender Simulation
Core logic: data loading, scoring, ranking, and explanation.
"""

import csv
from dataclasses import dataclass
from typing import List, Dict, Tuple


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a listener's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# OOP Recommender (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """
    Content-based music recommender.

    Scoring weights
    ---------------
    Genre match      : +2.5 pts  (strongest signal of taste)
    Mood match       : +1.5 pts  (important for the listener's current vibe)
    Energy proximity : 0–1.5 pts (1.5 × (1 - |target - song|))
    Acoustic bonus   : +0.5 pts  (if user likes acoustic AND song.acousticness > 0.6)
    Valence boost    : 0–0.5 pts (happier = slightly preferred, weighted lightly)
    """

    GENRE_WEIGHT = 2.5
    MOOD_WEIGHT = 1.5
    ENERGY_WEIGHT = 1.5
    ACOUSTIC_BONUS = 0.5
    VALENCE_WEIGHT = 0.5

    def __init__(self, songs: List[Song]):
        self.songs = songs

    # ------------------------------------------------------------------
    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Return (numeric_score, list_of_reason_strings) for one song."""
        score = 0.0
        reasons: List[str] = []

        # Genre match
        if song.genre.lower() == user.favorite_genre.lower():
            score += self.GENRE_WEIGHT
            reasons.append(f"genre match '{song.genre}' (+{self.GENRE_WEIGHT})")

        # Mood match
        if song.mood.lower() == user.favorite_mood.lower():
            score += self.MOOD_WEIGHT
            reasons.append(f"mood match '{song.mood}' (+{self.MOOD_WEIGHT})")

        # Energy proximity  (closer = more points, max 1.5)
        energy_gap = abs(user.target_energy - song.energy)
        energy_pts = round(self.ENERGY_WEIGHT * (1.0 - energy_gap), 3)
        score += energy_pts
        reasons.append(f"energy proximity (+{energy_pts:.2f})")

        # Acoustic preference
        if user.likes_acoustic and song.acousticness > 0.6:
            score += self.ACOUSTIC_BONUS
            reasons.append(f"acoustic match ({song.acousticness:.2f}) (+{self.ACOUSTIC_BONUS})")
        elif not user.likes_acoustic and song.acousticness < 0.4:
            score += self.ACOUSTIC_BONUS
            reasons.append(f"low acousticness ({song.acousticness:.2f}) (+{self.ACOUSTIC_BONUS})")

        # Valence (positivity) soft boost
        valence_pts = round(self.VALENCE_WEIGHT * song.valence, 3)
        score += valence_pts
        reasons.append(f"valence boost (+{valence_pts:.2f})")

        return round(score, 3), reasons

    # ------------------------------------------------------------------
    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by score (highest first)."""
        scored = [(self._score(user, s)[0], s) for s in self.songs]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:k]]

    # ------------------------------------------------------------------
    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        score, reasons = self._score(user, song)
        lines = [f"'{song.title}' scored {score:.2f} points because:"]
        for r in reasons:
            lines.append(f"  • {r}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Functional API (required by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file and return a list of dicts with typed values.
    Numeric columns are cast to float; id is cast to int.
    """
    songs: List[Dict] = []
    numeric_cols = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in numeric_cols:
                if col in row:
                    row[col] = float(row[col])
            row["id"] = int(row["id"])
            songs.append(dict(row))

    print(f"Loaded {len(songs)} songs from '{csv_path}'.")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.

    Returns
    -------
    (score: float, reasons: List[str])
    """
    score = 0.0
    reasons: List[str] = []

    GENRE_W   = 2.5
    MOOD_W    = 1.5
    ENERGY_W  = 1.5
    ACOUSTIC_BONUS = 0.5
    VALENCE_W = 0.5

    # Genre
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += GENRE_W
        reasons.append(f"genre match '{song['genre']}' (+{GENRE_W})")

    # Mood
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += MOOD_W
        reasons.append(f"mood match '{song['mood']}' (+{MOOD_W})")

    # Energy proximity
    target_e = float(user_prefs.get("energy", 0.5))
    gap = abs(target_e - float(song.get("energy", 0.5)))
    e_pts = round(ENERGY_W * (1.0 - gap), 3)
    score += e_pts
    reasons.append(f"energy proximity (+{e_pts:.2f})")

    # Acoustic
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
    acousticness = float(song.get("acousticness", 0.0))
    if likes_acoustic and acousticness > 0.6:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic match ({acousticness:.2f}) (+{ACOUSTIC_BONUS})")
    elif not likes_acoustic and acousticness < 0.4:
        score += ACOUSTIC_BONUS
        reasons.append(f"low acousticness ({acousticness:.2f}) (+{ACOUSTIC_BONUS})")

    # Valence
    v_pts = round(VALENCE_W * float(song.get("valence", 0.5)), 3)
    score += v_pts
    reasons.append(f"valence boost (+{v_pts:.2f})")

    return round(score, 3), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Score and rank all songs, returning the top-k as (song, score, explanation).

    Uses sorted() (non-mutating) so the original list is preserved.
    """
    scored = []
    for song in songs:
        sc, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, sc, explanation))

    # sorted() returns a new list — original `songs` is untouched
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]