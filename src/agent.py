import json
from urllib import response

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
Genres = ["pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop", "hip-hop", "classical", "r&b", "country", "metal", "folk", "edm", "reggae"]
Moods = ["happy", "chill", "intense", "relaxed", "moody", "focused", "confident", "peaceful", "romantic", "nostalgic", "angry", "sad", "euphoric", "uplifting"]

def sentence_to_profile(sentence):
    prompt = f"Genres:{Genres} Moods: {Moods} User request: {sentence} Please pick one genre, one mood, and calculate the value of energy to be between 0 and 1. Then return the answer as a dictionary(make sure to only use words that exist in the lists)"
    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
    )
    text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)
if __name__ == "__main__":
    print(sentence_to_profile("I want to listen to some music that will help me focus while I work on my project."))
# print(type(sentence_to_profile("I want to listen to some music that will help me focus while I work on my project.")))
