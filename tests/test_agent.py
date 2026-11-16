from unittest.mock import MagicMock, patch

# src/agent.py creates a Gemini client when imported; swap in a fake one so no API key or network is needed.
with patch("google.genai.Client", MagicMock()):
    from src.agent import mood_matches, pick_best


# Same mood in profile and song should count as a match.
def test_mood_matches_true():
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"title": "Sunny Day", "mood": "happy"}
    assert mood_matches(profile, song) is True


# Different moods should not count as a match.
def test_mood_matches_false():
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"title": "Rainy Night", "mood": "sad"}
    assert mood_matches(profile, song) is False


# pick_best should skip the higher-ranked song with the wrong mood and return the first one that matches.
def test_pick_best_prefers_mood_match():
    profile = {"genre": "pop", "mood": "chill", "energy": 0.4}
    first = ({"title": "Loud Song", "mood": "intense"}, 0.9, "top score")
    second = ({"title": "Calm Song", "mood": "chill"}, 0.7, "mood fits")
    recs = [first, second]
    assert pick_best(profile, recs) == second


# When no song matches the mood, pick_best should fall back to the first (top-scoring) tuple.
def test_pick_best_falls_back_to_first():
    profile = {"genre": "pop", "mood": "sad", "energy": 0.9}
    first = ({"title": "Happy Tune", "mood": "happy"}, 0.9, "top score")
    second = ({"title": "Angry Tune", "mood": "angry"}, 0.6, "second")
    recs = [first, second]
    assert pick_best(profile, recs) == first
