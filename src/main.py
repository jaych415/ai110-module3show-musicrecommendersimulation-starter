"""
main.py — CLI runner for the Music Recommender Simulation.

Demonstrates recommendations for three diverse user profiles.
Run with:  python main.py
"""

from src.recommender import load_songs, recommend_songs

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


def print_recommendations(profile_name: str, recs) -> None:
    print(f"\n{'='*55}")
    print(f"  Profile: {profile_name}")
    print(f"{'='*55}")
    for i, (song, score, explanation) in enumerate(recs, start=1):
        print(f"\n#{i}  {song['title']} — {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}"
              f"  |  Energy: {song['energy']}")
        print(f"    Score: {score:.2f}")
        print(f"    Because: {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")


    for profile_name, prefs in PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(profile_name, recs)

    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    main()