from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

GENRE_NEIGHBORS = {
    "pop":        ["indie pop", "dance pop", "electropop"],
    "rock":       ["indie rock", "alternative", "classic rock"],
    "hip-hop":    ["rap", "trap", "r&b"],
    "electronic": ["edm", "house", "techno", "synth-pop"],
    "jazz":       ["blues", "soul", "bossa nova"],
    "classical":  ["orchestral", "acoustic"],
    "r&b":        ["soul", "hip-hop", "funk"],
}

MOOD_NEIGHBORS = {
    "happy":      ["energetic", "uplifting", "euphoric"],
    "sad":        ["melancholic", "somber", "nostalgic"],
    "calm":       ["relaxed", "peaceful", "chill"],
    "energetic":  ["happy", "intense", "hype"],
    "romantic":   ["sensual", "calm", "dreamy"],
    "angry":      ["intense", "aggressive"],
}

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []

    # Rule 1: Genre match (max 2.0)
    user_genre = user_prefs.get("genre", "")
    song_genre = song["genre"]
    if song_genre == user_genre:
        score += 2.0
        reasons.append(f"genre match (+2.0)")
    elif song_genre in GENRE_NEIGHBORS.get(user_genre, []):
        score += 1.0
        reasons.append(f"similar genre to {user_genre} (+1.0)")

    # Rule 2: Mood match (max 1.5)
    user_mood = user_prefs.get("mood", "")
    song_mood = song["mood"]
    if song_mood == user_mood:
        score += 1.5
        reasons.append(f"mood match (+1.5)")
    elif song_mood in MOOD_NEIGHBORS.get(user_mood, []):
        score += 0.75
        reasons.append(f"close mood to {user_mood} (+0.75)")
    # Rule 3: Energy proximity (max 1.0)
    user_energy = user_prefs.get("energy", 0.5)
    energy_score = round(1.0 * (1 - abs(user_energy - song["energy"])), 2)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score})")

    # Rule 4: Valence proximity (max 0.5)
    user_valence = user_prefs.get("valence", 0.5)
    valence_score = round(0.5 * (1 - abs(user_valence - song["valence"])), 2)
    score += valence_score
    reasons.append(f"valence proximity (+{valence_score})")

    # Rule 5: Acousticness match (max 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic and song["acousticness"] >= 0.6:
        score += 0.5
        reasons.append("acoustic preference match (+0.5)")
    elif not likes_acoustic and song["acousticness"] < 0.4:
        score += 0.5
        reasons.append("electronic preference match (+0.5)")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort by score descending, and return the top k results."""
    # Step 1: Judge every song using score_song as the scoring function
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    # Step 2: Sort the entire list by score, highest first
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    # Step 3: Return only the top k results
    return ranked[:k]