import json
# Logging lets us record bad Gemini replies without printing them.
import logging

from src.recommender import load_songs, recommend_songs

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
# Logger for this file, used by sentence_to_profile.
logger = logging.getLogger(__name__)
Genres = ["pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop", "hip-hop", "classical", "r&b", "country", "metal", "folk", "edm", "reggae"]
Moods = ["happy", "chill", "intense", "relaxed", "moody", "focused", "confident", "peaceful", "romantic", "nostalgic", "angry", "sad", "euphoric", "uplifting"]

def sentence_to_profile(sentence):
    prompt = f"Genres:{Genres} Moods: {Moods} User request: {sentence} Please pick one genre, one mood, and calculate the value of energy to be between 0 and 1. Then return the answer as a dictionary(make sure to only use words that exist in the lists)"
    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
    )
    # Keep only the part from the first "{" to the last "}", so code fences or extra words are dropped.
    raw_text = response.text
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1:
        logger.warning("No JSON object found in Gemini reply. Raw text: %r", raw_text)
        return None
    text = raw_text[start:end + 1]

    # Try to parse the reply; if it isn't valid JSON, log the raw text and give up.
    try:
        profile = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Could not parse Gemini reply as JSON. Raw text: %r", text)
        return None

    # Make sure the reply is a dictionary before reading keys from it.
    if not isinstance(profile, dict):
        logger.warning("Gemini reply was not a dictionary. Raw text: %r", text)
        return None

    # Check genre and mood are from our allowed lists.
    if profile.get("genre") not in Genres:
        logger.warning("Invalid genre %r. Raw text: %r", profile.get("genre"), text)
        return None
    if profile.get("mood") not in Moods:
        logger.warning("Invalid mood %r. Raw text: %r", profile.get("mood"), text)
        return None

    # Check energy is a real number (not True/False) between 0 and 1.
    energy = profile.get("energy")
    if isinstance(energy, bool) or not isinstance(energy, (int, float)) or not 0 <= energy <= 1:
        logger.warning("Invalid energy %r. Raw text: %r", energy, text)
        return None

    return profile
# Check whether a song's mood is the same as the mood in the profile.
def mood_matches(profile, song):
    return profile["mood"] == song["mood"]

# Return the first recommendation whose mood matches the profile, or the top one if none match.
def pick_best(profile, recs):
    for rec in recs:
        if mood_matches(profile, rec[0]):
            return rec
    return recs[0]

if __name__ == "__main__":
    profile = {"genre": "pop", "mood": "sad", "energy": 0.9}
    songs = load_songs("data/songs.csv")
    recs = recommend_songs(profile, songs, k=5)
    print(pick_best(profile, recs)[0]["title"])
    print(sentence_to_profile("I want to listen to some music that will help me focus while I work on my project."))
# print(type(sentence_to_profile("I want to listen to some music that will help me focus while I work on my project.")))
