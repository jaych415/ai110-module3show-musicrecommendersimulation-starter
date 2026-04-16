🎧 Model Card: Music Recommender Simulation
1. Model Name
VibeFinder 1.0

2. Intended Use
VibeFinder is a classroom simulation of a content-based music recommender. It suggests up to five songs from a small fixed catalog based on a user's stated preferences for genre, mood, energy level, and acoustic texture. It is intended for educational exploration of how real-world recommender systems work — not for use in a production product or with real listeners.
The model assumes users can clearly articulate a preferred genre and mood, and that those preferences are stable (it has no memory of past sessions).

3. How the Model Works
Every song in the catalog carries a set of descriptive numbers: how energetic it is (0 = very calm, 1 = very intense), how positive-sounding it is (valence), and how acoustic it sounds. It also has text labels for genre and mood.
When a user provides their preferences, the system goes through every song and gives it a score:

It awards the most points (2.5) for matching the user's favorite genre, because genre is the strongest predictor of whether someone will enjoy a song.
It awards the next most points (1.5) for matching the user's preferred mood.
It computes how close the song's energy level is to the user's target and awards up to 1.5 additional points — the closer the match, the higher the score.
It gives a small bonus (0.5) if the user's acoustic preference aligns with the song's acousticness.
It adds a tiny positivity boost (up to 0.5) based on valence, reflecting a slight preference for upbeat-sounding songs.

Once every song has a score, the list is sorted from highest to lowest and the top songs are returned with a plain-English explanation of what drove each score.

4. Data
The catalog contains 20 songs across 10 genres: pop, lofi, rock, indie pop, synthwave, ambient, jazz, acoustic, EDM, bossa nova, and country. Each song has 10 attributes: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.
Mood labels present: happy, chill, intense, relaxed, moody, focused, energetic.
What's missing: No songs carry a "sad" or "melancholic" mood label, so a user with a sad preference will never receive a mood-match bonus. Genres like hip-hop, R&B, classical, and metal are absent entirely. The dataset skews toward Western contemporary music and would not serve users with different cultural tastes well.

5. Strengths

For users with a clear, strongly-represented preference (e.g., lofi/chill or rock/intense), the top results feel accurate and match intuition immediately.
The explanation system makes the scoring transparent — you can see exactly why each song ranked where it did.
The energy proximity formula rewards nuance: a song at 0.78 beats a song at 0.60 for a user targeting 0.80, which mirrors how listeners actually think about vibe.


6. Limitations and Bias
Genre dominance: With a weight of 2.5, genre matching is so powerful that a perfect genre match with a terrible mood and energy match can still outscore a near-perfect match in another genre. This creates a subtle "genre bubble" — users are unlikely to discover cross-genre songs they might love.
Small catalog: With only 20 songs, the rock profile always returns the same three rock tracks. Diversity is structurally impossible at this scale.
Missing moods and genres: Users who prefer sad, melancholic, or aggressive music will never see a mood-match bonus because those labels don't exist in the dataset. Their recommendations will default to energy- and valence-driven results, which may feel off.
Acoustic binary: The likes_acoustic field is a simple true/false. Real listeners have a spectrum of preferences — someone might enjoy lightly acoustic pop but dislike full acoustic folk. The current model cannot distinguish this.
No demographic or cultural representation: All songs are implicitly from a Western popular-music context. A listener whose taste centers on non-Western genres would receive no meaningful matches.

7. Evaluation
Three user profiles were tested:

Happy Pop Fan (genre=pop, mood=happy, energy=0.8): Top result was "Sunrise City" with a score of 6.39 — genre, mood, and energy all matched well. This felt correct intuitively.
Chill Lofi Listener (genre=lofi, mood=chill, energy=0.38, likes_acoustic=True): Top two results were lofi/chill songs with acoustic bonuses. The third was a non-chill lofi track, which makes sense — genre weight is strong enough to surface it even without a mood match.
Intense Rock Head (genre=rock, mood=intense, energy=0.92): All three rock/intense songs floated to the top with near-identical scores (6.22, 6.17, 6.14). The tiny differences came from energy gap and valence — highlighting how the catalog's limited rock selection makes the recommender feel repetitive.

Surprise: "Gym Hero" (pop/intense) kept appearing for the Rock Head profile because mood and energy were strong matches even without a genre hit. This is actually reasonable behavior — a gym playlist user might not care about genre labels.
Adversarial profile tested: energy=0.9, mood=sad — no mood bonus ever fired; the system returned high-energy tracks without acknowledging the emotional mismatch. A real system would need to handle this gracefully.

8. Future Work

Add tempo and danceability to scoring: These features are loaded but currently unused. A user who wants to dance would benefit from danceability weighting.
Soften the genre dominance: Reducing genre weight to ~1.5 and increasing energy and mood weights would encourage cross-genre discovery.
Expand the catalog: Even 100 songs across 20 genres would dramatically improve diversity in results.
Multi-mood profiles: Allow users to specify "energetic in the morning, chill at night" so the system can recommend based on time of day or context.
Collaborative signals: Combine content-based scores with "users who liked X also liked Y" logic to surface surprising but accurate recommendations.


9. Personal Reflection
The most surprising part of this project was how quickly a simple set of weights can produce results that feel intelligent — even when the underlying logic is just arithmetic. Once genre and mood matched, the score jumped high enough that the other features barely mattered, which mirrors exactly how "filter bubbles" form on real platforms: the algorithm confidently serves you more of what you already told it you like.
Building this also made me appreciate why companies like Spotify invest so heavily in data diversity. With 20 songs, the recommender's limitations are obvious at a glance. At 100 million songs, those same structural biases become invisible — and far more consequential, shaping what music entire populations discover or never hear.
