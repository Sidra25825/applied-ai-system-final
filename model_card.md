# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeFinder 1.0

---

## 2. Intended Use  

This recommender suggests songs from a small catalog based on a user's favorite genre, favorite mood, and target energy. It assumes the user can describe their taste with these three things. It is made for classroom learning, not for real users. It should not be used to make real product decisions or to represent a person's full musical taste.

---

## 3. How the Model Works  

This recommender is content-based, which means it compares each song's attributes to the user's taste profile instead of looking at what other people listen to. A song gets 2 points if its genre matches the user's favorite genre and 1 point if its mood matches the user's favorite mood. It also gets up to 1 more point for energy: the closer the song's energy is to the energy the user wants, the closer it gets to that full point. This means the highest score any song can get is 4. The recommender scores every song in the catalog, then sorts them from highest to lowest score. It returns the top few songs along with the reasons each one earned its points.

---

## 4. Data  

The catalog is data/songs.csv with 18 songs: 10 from the starter file and the rest added by me. Each song has a genre, mood, energy, tempo, valence, danceability, and acousticness. The recommender only uses genre, mood, and energy. The catalog is small, and some genres (like rock) have only one song. Many parts of musical taste are missing, such as language, lyrics, and era.

---

## 5. Strengths  

The system works best when the catalog has several songs that fit the user's genre and mood. For "Chill Lofi", the top results were three lofi songs, and Library Rain scored the maximum 4.00. The reasons shown with each score make it easy to see why a song was recommended.

---

## 6. Limitations and Bias 

The catalog has only one rock song, so the "Deep Intense Rock" profile gets one great match and then mostly weak ones. Storm Runner scored 3.99, but the next result, Gym Hero, only matched the mood, and the last three only matched on energy and scored under 1.0. Because a genre match is worth the most points (+2.0), the system favors songs from the user's genre and has little to offer when that genre has few songs. Gym Hero (a pop song with an intense mood) showed up for both "High-Energy Pop" and "Deep Intense Rock" because its energy is high.

---

## 7. Evaluation  

I tested 7 user profiles: Default (pop, happy), High-Energy Pop,
Chill Lofi, Deep Intense Rock, Sad but Energetic, Unknown Genre
(classical), and Middle of Road (jazz). I looked at whether the
top 5 songs matched each profile's genre, mood, and energy, and
whether the reasons made sense. What surprised me most was "Sad
but Energetic": the top two songs were pop songs that are not sad,
and the only sad song ranked third, because a genre match is worth
more than a mood match.

**Weight shift experiment:** I halved the genre weight (from +2.0 to +1.0) and doubled the energy weight (energy points went from 1 minus the gap to 2 times that). For the "Sad but Energetic" profile (pop, sad, energy 0.9), the original top 3 were Gym Hero, Sunrise City, and Empty Porch Light, the only sad song. After the change, Empty Porch Light dropped out of the top 5, because energy mattered even more, and the mood match was worth relatively less next to it. For the Default profile, Rooftop Lights (happy) moved above Gym Hero (intense), which fits the user better. My conclusion is that the change made the rankings different, not more accurate, so I reverted the weights to the original values.

**Profile Comparisons:**

1. **High-Energy Pop vs Chill Lofi:** The top songs moved from high-energy pop songs (Sunrise City, Gym Hero) to low-energy lofi songs (Library Rain, Midnight Coding). This makes sense because both the genre and the energy target changed.
2. **High-Energy Pop vs Deep Intense Rock:** Gym Hero appears in both lists. It matches the pop genre for the first profile and the "intense" mood for the second, and its energy is high for both.
3. **Chill Lofi vs Deep Intense Rock:** These profiles want opposite energy levels. Lofi has several good matches, but rock has only one genre match (Storm Runner) because the dataset has only one rock song.
4. **High-Energy Pop vs Sad but Energetic:** The top 2 are the same two songs (Gym Hero and Sunrise City) because the genre match (+2.0) is worth more than the mood. Only the third result changes: Rooftop Lights (happy) is replaced by Empty Porch Light (sad).
5. **Unknown Genre vs Middle of Road:** Each profile has one genre match: Moonlit Sonata Sketch for classical and Coffee Shop Stories for jazz. After that, Middle of Road relies on energy closeness only, while Unknown Genre's next three songs also get a mood match because they are "chill".

---

## 8. Future Work  

1. Add more songs, so every genre has several options.
2. Use more features, like valence and acousticness, and let users pick several favorite genres or moods.
3. Add a diversity rule, so the top results don't all come from the same genre, and lower the genre weight so mood can matter more.

---

## 9. Personal Reflection  

The most interesting thing I discovered was how apps like YouTube
and Spotify decide which songs I might like. I learned that there
are two main techniques: collaborative filtering, which looks at
what similar users do, and content-based filtering, which looks at
the song's own attributes. YouTube mostly relies on watch behavior,
while Spotify mixes both, and my project uses only the content-based
type. This was my biggest learning moment.

AI helped me mostly with writing and documentation. When I finished
a piece of work, I asked it to add the explanation to the README or
the model card. After that, I went back to the file and checked what
it wrote to see if it was correct, for example when we summarized my
scoring algorithm.

What surprised me was that my recommender only adds up points, yet
for the "Chill Lofi" profile it returned calm lofi songs that felt
like real recommendations.

Next, I would add more songs so every genre has several options,
and use more features like valence and acousticness.

---

## 10. Collaboration with AI: A Suggestion I Changed

While building src/agent.py, the AI assistant suggested cleaning Gemini's reply with this line:

```python
text = response.text.replace("```json", "").replace("```", "").strip()
```

It worked in my first runs, so I used it. Later, the program crashed with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. When I logged the raw reply, I saw that Gemini had wrapped the JSON in a code fence labeled "python" instead of "json". My replace calls only removed "```json", so the word "python" stayed at the start of the text.

I did not keep the replace approach, because it only works for the exact fence labels I thought of. I changed it so the code finds the first "{" with `find` and the last "}" with `rfind`, keeps only the text between them, and then validates the result. Everything outside the braces gets dropped. This is better because it doesn't depend on which label or extra words Gemini adds, and it is still simple: a few lines and no new library.

What I learned: a suggestion can work in my first tests and still be fragile. I should test with messy input and read the raw reply before trusting a cleanup step.

---

## 11. Collaboration with AI: A Suggestion I Accepted

My original recommender had a known bias: a genre match is worth +2.0, but a mood match is only worth +1.0. Because of this, for "Sad but Energetic" the top two songs were pop songs that are not sad, and the only sad song ranked third.

The AI assistant suggested a small check after scoring: look through the top 5 songs and pick the first one whose mood matches the profile, and fall back to the top-scored song if none match. This became `pick_best`, which uses `mood_matches`. I accepted it as suggested and wired it into src/main.py as an extra "Agent pick" line.

I accepted it because it targets the exact bias I had already found. It is also short and easy to read (one loop), and it doesn't change any score, so the original recommender stays intact.

I tested it. For "Sad but Energetic", the pick changed from Gym Hero to Empty Porch Light. Across the 8 profiles, the pick changed in 2 (Sad but Energetic and Unknown Genre), and the picked song's mood matched in all 8.

One downside I noticed: for "Unknown Genre", the agent skipped the only classical song to get a mood match, which is not clearly better.

---

## 12. Limitations and Bias of the Agent

Adding the agent did not remove my recommender's original bias. A genre match is still worth more than a mood match. `pick_best` only partly offsets this, and only inside the top 5 songs. If no song with the right mood makes the top 5, the bias wins.

`pick_best` also puts mood first, which is debatable. For "Unknown Genre", it skipped the only classical song to get a mood match.

The "From Sentence" profile depends on Gemini, which is not fully deterministic. The same sentence gave different top results in two runs.

If the Gemini API call itself fails, for example with no network or a bad key, `sentence_to_profile` does not catch that error, so the program stops. Only bad replies are handled.

The catalog is small (18 songs), and the allowed genre and mood lists only contain words from the catalog.

Finally, my automated tests don't cover the live Gemini call or the guardrail branches inside `sentence_to_profile`.

---

## 13. Could the AI Be Misused, and How I Prevent It

**Protections that are already in the code:**

- Gemini's reply is validated before it reaches the recommender. Genre must be in the allowed list, mood must be in the allowed list, and energy must be a number from 0 to 1.
- Bad replies are logged as a warning and skipped, so they never get scored.
- The API key lives in a `.env` file, which is listed in `.gitignore`, and the code never prints it.

**Risks that are NOT handled yet:**

- The user's sentence goes directly into the prompt. Someone could type instructions meant to confuse the model. The validator should limit the damage, because only allowed words can pass, but I did not test this.
- There is no limit on input length or on the number of requests, so someone could run up API usage.
- The project has no user accounts and no privacy features.

---

## 14. What Surprised Me While Testing

What surprised me most was the "Unknown Genre" profile: `{"genre": "classical", "mood": "chill", "energy": 0.2}`.

The top-scored song was Moonlit Sonata Sketch, a classical song with the mood "peaceful". The agent skipped it and picked Spacewalk Thoughts, an ambient song with the mood "chill". I expected the classical song to come first, because the user asked for classical and "peaceful" fits the request.

The reason is that `mood_matches` compares the mood words exactly. So "peaceful" and "chill" count as different, even though they are close in meaning.

This means the agent fixed the "Sad but Energetic" case (Gym Hero changed to Empty Porch Light) but arguably made "Unknown Genre" worse.

What I learned: a simple exact-match rule can be too literal, and a change that helps one case can hurt another. So I should test several profiles, not just one.
