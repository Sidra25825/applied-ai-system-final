# 🎵 Music Recommender + Gemini Agent

**Base project:** this repo extends **"Music Recommender Simulation"** (CodePath AI110, Module 3). The original project was a small content-based music recommender: it represents songs and a user "taste profile" as data and scores each song by genre match (+2.0), mood match (+1.0), and energy closeness (up to +1.0). It then returns the top-k songs, each with the reasons behind its score.

---

## Title and Summary: What This Version Adds

This version adds an **Agentic Workflow** on top of the original recommender:

1. **Sentence → profile.** [src/agent.py](src/agent.py) sends a plain-English sentence (for example *"calm and relaxing music to help me focus while I work on my project."*) to Gemini through the `google-genai` package. Gemini returns a taste profile: one genre, one mood, and an energy value.
2. **Validate.** The agent does not trust that reply blindly. It extracts the JSON, checks every field against allowed values, and returns `None` if anything is wrong.
3. **Score.** The existing recommender ([src/recommender.py](src/recommender.py)) scores every song for that profile and keeps the top 5.
4. **Check and pick.** `pick_best` looks through the top 5 and picks the first song whose mood matches the profile. If none match, it keeps the top-scored song.

This is wired into [src/main.py](src/main.py), and it changes what the program prints. Every profile now ends with an **`Agent pick: <title> (mood match: True/False)`** line, and there is a new **"From Sentence"** profile built by Gemini.

**Why it matters:** users describe what they want in words, not as `{"genre": "lofi", "mood": "focused", "energy": 0.25}`. The agent lets a language model handle that translation. Plain code then checks the model's answer and catches cases where the scoring rule's genre bias pushes a wrong-mood song to the top.

### Original Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version is a content-based music recommender. It scores each song by genre match (+2.0), mood match (+1.0), and energy closeness (up to 1.0), then returns the top songs with the reasons for each score.

---

## Architecture Overview

The full diagram is in [diagrams/architecture.mmd](diagrams/architecture.mmd) (Mermaid source; it renders on GitHub or in any Mermaid viewer).

How data flows through it:

- **Input → Gemini:** the user's sentence goes to `sentence_to_profile` in `src/agent.py`, which sends a prompt to Gemini and receives text back.
- **Guardrails (inside `sentence_to_profile`):** the reply must pass two checks. First, a `{ ... }` block must be found and parse as JSON. Second, `genre` must be in the `Genres` list, `mood` in the `Moods` list, and `energy` a number from 0 to 1. If either check fails, the function logs a warning and returns `None`, and `main.py` skips that profile.
- **Taste profile:** a valid profile (or one of the 7 hard-coded profiles in `main.py`) goes to `recommend_songs`. It calls `score_song` on every song loaded from `data/songs.csv` and returns the top 5.
- **Agent pick:** `pick_best` receives both the profile and the top 5, and uses `mood_matches` to choose the first song whose mood matches.
- **Output and human check:** `main.py` prints the top 5 plus the `Agent pick` line. A human (the user) reads it and judges whether the pick actually fits; no code does that step.
- **Testing:** pytest checks `mood_matches` and `pick_best` (`tests/test_agent.py`) and the `Recommender` class (`tests/test_recommender.py`). No test calls Gemini.

---

## How The System Works

Real-world music apps like Spotify use two main ideas to recommend songs. **Collaborative filtering** looks at what other users do: if people who like the same songs as you also love a new song, you will probably like it too. **Content-based filtering** looks at the songs themselves, using attributes like tempo, mood, and energy to find songs similar to the ones you already enjoy. Big apps mix both and learn from your likes, skips, saved songs, and playlists. My version is **content-based**: it gives each song a score based on how well its genre matches, how well its mood matches, and how close its energy is to what the user wants.

**Features used**

- `Song`
  - `genre`, `mood`, `energy`
  - Also available: `tempo_bpm`, `valence`, `danceability`, `acousticness`
- `UserProfile`
  - `favorite_genre`, `favorite_mood`, `target_energy`

**Algorithm Recipe**

Each song gets a score by adding up these points:

- **+2.0 points** if the song's genre matches the user's favorite genre
- **+1.0 point** if the song's mood matches the user's favorite mood
- **Energy points** = `1 - abs(user target energy - song energy)` (the closer the energy, the more points, up to 1.0)
- **Maximum score: 4.0**

**Expected Bias**

This system might over-prioritize genre, because a genre match is worth the most points. A song that matches the user's mood and energy perfectly but has a different genre can score at most 2.0, while a song that only matches the genre already gets 2.0 before its energy points are added. So the system may ignore good songs from other genres.

---

## Getting Started

### Setup

1. **Create and activate a virtual environment.**

   Windows (PowerShell):

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Mac or Linux:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies** (`pandas`, `pytest`, `streamlit`, `python-dotenv`, `google-genai`):

   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Gemini API key.** Create a file named `.env` in the project root (next to `requirements.txt`) containing one line:

   ```text
   GEMINI_API_KEY=your_key
   ```

   Replace `your_key` with your own key. Never commit a real key: `.env` is listed in `.gitignore`, so git ignores it. `src/agent.py` loads it with `python-dotenv`.

4. **Run the app** from the project root:

   ```bash
   python -m src.main
   ```

### Running Tests

Run the tests from the project root with:

```bash
python -m pytest
```

Use `python -m pytest`, not plain `pytest`. Plain `pytest` fails during collection with `ModuleNotFoundError: No module named 'src'`, because it does not add the project root to Python's import path. The tests do not need a Gemini API key.

You can add more tests in `tests/test_recommender.py` and `tests/test_agent.py`.

---

## Sample Interactions

All three examples are copied from real runs.

### (a) "Sad but Energetic": the agent overrides the top score

Input profile (hard-coded in `src/main.py`):

```python
{"genre": "pop", "mood": "sad", "energy": 0.9}
```

Output of `python -m src.main` for this profile:

```text
=== Sad but Energetic ===

Top recommendations:

Gym Hero - Score: 2.97
Because: genre match (+2.0), energy closeness (+0.97)

Sunrise City - Score: 2.92
Because: genre match (+2.0), energy closeness (+0.92)

Empty Porch Light - Score: 1.35
Because: mood match (+1.0), energy closeness (+0.35)

Storm Runner - Score: 0.99
Because: energy closeness (+0.99)

Neon Skyline Drop - Score: 0.95
Because: energy closeness (+0.95)

Agent pick: Empty Porch Light (mood match: True)
```

The scoring rule put Gym Hero first because of the genre bonus, but Gym Hero is not sad. The agent passed over the two higher-scored songs and picked Empty Porch Light, the only sad song in the top 5.

### (b) "From Sentence": Gemini builds the profile

Input sentence (in `src/main.py`):

```text
calm and relaxing music to help me focus while I work on my project.
```

`main.py` does not print the profile Gemini returns. To see it, I called `sentence_to_profile` directly with the same sentence, then ran the same `recommend_songs` and `pick_best` steps:

```text
Input sentence: calm and relaxing music to help me focus while I work on my project.
Profile from Gemini: {'genre': 'lofi', 'mood': 'focused', 'energy': 0.25}
Loading songs from data/songs.csv...
Focus Flow - Score: 3.85
Library Rain - Score: 2.90
Midnight Coding - Score: 2.83
Empty Porch Light - Score: 1.00
Spacewalk Thoughts - Score: 0.97
Agent pick: Focus Flow (mood match: True)
```

The "From Sentence" block from a separate run of `python -m src.main` (a separate Gemini call) gave the same top 5:

```text
=== From Sentence ===

Top recommendations:

Focus Flow - Score: 3.85
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.85)

Library Rain - Score: 2.90
Because: genre match (+2.0), energy closeness (+0.90)

Midnight Coding - Score: 2.83
Because: genre match (+2.0), energy closeness (+0.83)

Empty Porch Light - Score: 1.00
Because: energy closeness (+1.00)

Spacewalk Thoughts - Score: 0.97
Because: energy closeness (+0.97)

Agent pick: Focus Flow (mood match: True)
```

Gemini's reply can differ between runs (see *Consistency* below), so your output for this profile may not match.

### (c) "Chill Lofi": the agent agrees with the top result

Input profile (hard-coded in `src/main.py`):

```python
{"genre": "lofi", "mood": "chill", "energy": 0.35}
```

Output of `python -m src.main` for this profile:

```text
=== Chill Lofi ===

Top recommendations:

Library Rain - Score: 4.00
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.00)

Midnight Coding - Score: 3.93
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.93)

Focus Flow - Score: 2.95
Because: genre match (+2.0), energy closeness (+0.95)

Spacewalk Thoughts - Score: 1.93
Because: mood match (+1.0), energy closeness (+0.93)

Coffee Shop Stories - Score: 0.98
Because: energy closeness (+0.98)

Agent pick: Library Rain (mood match: True)
```

The top-scored song already matches the mood, so the agent keeps it.

---

## Sample Recommendation Output

This is the output of `python -m src.main` for the default profile: genre pop, mood happy, energy 0.8.

```text
Loading songs from data/songs.csv...

Top recommendations:

Sunrise City - Score: 3.98
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.98)

Gym Hero - Score: 2.87
Because: genre match (+2.0), energy closeness (+0.87)

Rooftop Lights - Score: 1.96
Because: mood match (+1.0), energy closeness (+0.96)

Crown the Block - Score: 0.98
Because: energy closeness (+0.98)

Night Drive Loop - Score: 0.95
Because: energy closeness (+0.95)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Evaluation: Profile Outputs

This is the full output of `python -m src.main` for all seven profiles.

*Note: this output was recorded before the agent was added. The scores and rankings are unchanged in the current version, but each profile now ends with an `Agent pick:` line, and an eighth profile, "From Sentence", is added. See [Reliability and Guardrails](#reliability-and-guardrails) for the agent picks.*

```text
Loading songs from data/songs.csv...

=== Default ===

Top recommendations:

Sunrise City - Score: 3.98
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.98)

Gym Hero - Score: 2.87
Because: genre match (+2.0), energy closeness (+0.87)

Rooftop Lights - Score: 1.96
Because: mood match (+1.0), energy closeness (+0.96)

Crown the Block - Score: 0.98
Because: energy closeness (+0.98)

Night Drive Loop - Score: 0.95
Because: energy closeness (+0.95)


=== High-Energy Pop ===

Top recommendations:

Sunrise City - Score: 3.92
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.92)

Gym Hero - Score: 2.97
Because: genre match (+2.0), energy closeness (+0.97)

Rooftop Lights - Score: 1.86
Because: mood match (+1.0), energy closeness (+0.86)

Storm Runner - Score: 0.99
Because: energy closeness (+0.99)

Neon Skyline Drop - Score: 0.95
Because: energy closeness (+0.95)


=== Chill Lofi ===

Top recommendations:

Library Rain - Score: 4.00
Because: genre match (+2.0), mood match (+1.0), energy closeness (+1.00)

Midnight Coding - Score: 3.93
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.93)

Focus Flow - Score: 2.95
Because: genre match (+2.0), energy closeness (+0.95)

Spacewalk Thoughts - Score: 1.93
Because: mood match (+1.0), energy closeness (+0.93)

Coffee Shop Stories - Score: 0.98
Because: energy closeness (+0.98)


=== Deep Intense Rock ===

Top recommendations:

Storm Runner - Score: 3.99
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.99)

Gym Hero - Score: 1.97
Because: mood match (+1.0), energy closeness (+0.97)

Neon Skyline Drop - Score: 0.95
Because: energy closeness (+0.95)

Iron Furnace - Score: 0.93
Because: energy closeness (+0.93)

Sunrise City - Score: 0.92
Because: energy closeness (+0.92)


=== Sad but Energetic ===

Top recommendations:

Gym Hero - Score: 2.97
Because: genre match (+2.0), energy closeness (+0.97)

Sunrise City - Score: 2.92
Because: genre match (+2.0), energy closeness (+0.92)

Empty Porch Light - Score: 1.35
Because: mood match (+1.0), energy closeness (+0.35)

Storm Runner - Score: 0.99
Because: energy closeness (+0.99)

Neon Skyline Drop - Score: 0.95
Because: energy closeness (+0.95)


=== Unknown Genre ===

Top recommendations:

Moonlit Sonata Sketch - Score: 2.98
Because: genre match (+2.0), energy closeness (+0.98)

Spacewalk Thoughts - Score: 1.92
Because: mood match (+1.0), energy closeness (+0.92)

Library Rain - Score: 1.85
Because: mood match (+1.0), energy closeness (+0.85)

Midnight Coding - Score: 1.78
Because: mood match (+1.0), energy closeness (+0.78)

Empty Porch Light - Score: 0.95
Because: energy closeness (+0.95)


=== Middle of Road ===

Top recommendations:

Coffee Shop Stories - Score: 3.87
Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.87)

Velvet Hours - Score: 0.98
Because: energy closeness (+0.98)

Dirt Road Summers - Score: 0.95
Because: energy closeness (+0.95)

Midnight Coding - Score: 0.92
Because: energy closeness (+0.92)

Focus Flow - Score: 0.90
Because: energy closeness (+0.90)
```

---

## Reliability and Guardrails

### How the agent validates Gemini's reply

`sentence_to_profile` in [src/agent.py](src/agent.py) never returns Gemini's raw text. In order, it:

1. Keeps only the text from the first `{` to the last `}`. If either brace is missing, it logs a warning and returns `None`.
2. Parses that text with `json.loads`. On `json.JSONDecodeError`, it logs a warning with the raw text and returns `None`.
3. Checks that the result is a dictionary.
4. Checks that `genre` is in the `Genres` list and `mood` is in the `Moods` list.
5. Checks that `energy` is a number (not `True`/`False`) from 0 to 1.

Any failure logs a warning through Python's `logging` module and returns `None`. In `main.py`, a profile that is `None` is skipped with a message, and the program keeps going.

**Evidence.** I ran `sentence_to_profile` four times. Each time, `unittest.mock.patch.object` replaced `client.models.generate_content` with a fake that returns the reply in the table, so Gemini was never called. No project files were edited. I printed each result:

| Faked Gemini reply | Result |
|---|---|
| `` ```python `` fence around `{"genre": "lofi", "mood": "focused", "energy": 0.4}` | parsed correctly |
| `Sorry, I can't help with that.` | warning + `None` |
| `{"genre": "polka", "mood": "happy", "energy": 0.5}` | warning + `None` |
| `{"genre": "pop", "mood": "happy", "energy": 1.7}` | warning + `None` |

Real output, in that order:

```text
{'genre': 'lofi', 'mood': 'focused', 'energy': 0.4}
No JSON object found in Gemini reply. Raw text: "Sorry, I can't help with that."
None
Invalid genre 'polka'. Raw text: '{"genre": "polka", "mood": "happy", "energy": 0.5}'
None
Invalid energy 1.7. Raw text: '{"genre": "pop", "mood": "happy", "energy": 1.7}'
None
```

### Real failure that motivated the fix

While testing, Gemini once wrapped its JSON in a Markdown code fence labeled `python` instead of `json`. My original cleanup only removed `` ```json `` and `` ``` ``, so the word `python` was left at the start of the text. `json.loads` then failed with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, and the program crashed.

The fix was to stop guessing which fence label Gemini would use. The function now extracts everything from the first `{` to the last `}`, so any wrapper text is dropped. The first row of the table above reproduces that kind of reply with a faked response and shows it now parses correctly. *(The original crashing Gemini reply was not saved, so the exact text of that reply is not verified; the fix is verified with the simulated reply.)*

### Guardrail test: invalid profile is skipped, no crash

To test the `None` path end to end, I ran `main()` from `src/main.py` while `unittest.mock.patch.object` replaced `sentence_to_profile` in `src.main` with a fake that returns `None`. That makes the "From Sentence" entry in the `profiles` dictionary `None`, exactly as if Gemini's reply had failed validation. No project files were edited, and Gemini was not called. The last lines of the output:

```text
Focus Flow - Score: 0.90
Because: energy closeness (+0.90)

Agent pick: Coffee Shop Stories (mood match: True)

Skipped profile From Sentence: the agent returned no valid profile.
```

The 7 hard-coded profiles printed normally (the last of them, "Middle of Road", ends with the Coffee Shop Stories pick above). The "From Sentence" profile was skipped with the message, and the process exited with code 0, with no crash.

The same check was also done earlier by temporarily replacing the "From Sentence" value in `src/main.py` with `None`. That run's output reportedly matched, but it was not saved, so that earlier run is *not verified* here.

### Consistency: Gemini is not fully deterministic

During development, the same sentence (*"calm and relaxing music to help me focus while I work on my project."*) produced different top results in two runs: Spacewalk Thoughts first in one run, Focus Flow first in another. So the "From Sentence" profile, and its recommendations, can change from run to run. *(The run with Spacewalk Thoughts first was observed earlier and is not reproduced in this README. The two runs captured while writing this README both returned Focus Flow first, as shown in Sample Interaction (b).)*

### How often the agent changed the pick

From the full `python -m src.main` run used for this README:

| Profile | Top-scored song | Agent pick | Mood match | Pick changed? |
|---|---|---|---|---|
| Default | Sunrise City | Sunrise City | True | No |
| High-Energy Pop | Sunrise City | Sunrise City | True | No |
| Chill Lofi | Library Rain | Library Rain | True | No |
| Deep Intense Rock | Storm Runner | Storm Runner | True | No |
| Sad but Energetic | Gym Hero | Empty Porch Light | True | **Yes** |
| Unknown Genre | Moonlit Sonata Sketch | Spacewalk Thoughts | True | **Yes** |
| Middle of Road | Coffee Shop Stories | Coffee Shop Stories | True | No |
| From Sentence | Focus Flow | Focus Flow | True | No |

In this run, the agent changed the pick in **2 of 8** profiles, and in **all 8** the picked song's mood matched the profile. Because "From Sentence" depends on Gemini, its row can change between runs.

---

## Testing Summary

Real output of `python -m pytest`:

```text
tests\test_agent.py ....                                                 [ 66%]
tests\test_recommender.py ..                                             [100%]

============================== 6 passed in 0.82s ==============================
```

**What the 4 new tests in [tests/test_agent.py](tests/test_agent.py) check:**

- `test_mood_matches_true`: `mood_matches` returns `True` when the profile and song have the same mood.
- `test_mood_matches_false`: `mood_matches` returns `False` when the moods differ.
- `test_pick_best_prefers_mood_match`: when the first song's mood doesn't match but the second does, `pick_best` returns the second tuple.
- `test_pick_best_falls_back_to_first`: when no song matches, `pick_best` returns the first (top-scored) tuple.

**No test calls Gemini.** Importing `src/agent.py` creates a Gemini client (`client = genai.Client()`), so `tests/test_agent.py` swaps in a fake client before importing it:

```python
with patch("google.genai.Client", MagicMock()):
    from src.agent import mood_matches, pick_best
```

`tests/test_recommender.py` does not import `src.agent` at all. To check that no API key is needed, I copied `src/`, `tests/` and `data/` (no `.env`) to an empty folder and ran `python -m pytest` there with `GEMINI_API_KEY` and `GOOGLE_API_KEY` unset:

```text
tests\test_agent.py ....                                                 [ 66%]
tests\test_recommender.py ..                                             [100%]

============================== 6 passed in 0.54s ==============================
```

As a control, in that same folder, `import src.agent` *without* the patch fails with `ValueError: No API key was provided.` So the patch is what makes the tests independent of the key.

**What is NOT tested:**

- The live Gemini call inside `sentence_to_profile`.
- The guardrail branches inside `sentence_to_profile` (missing braces, bad JSON, non-dictionary reply, invalid genre/mood/energy). I checked them by hand, as shown under Reliability and Guardrails, but there are no automated pytest tests for them.
- The skip logic in `main.py` (checked by hand only).
- `recommend_songs` and `score_song`, which `main.py` actually uses. The 2 tests in `tests/test_recommender.py` test the `Recommender` class (`recommend` and `explain_recommendation`), which is still a starter stub and is not used by `main.py`.

---

## Experiments You Tried

I halved the genre weight (+2.0 to +1.0) and doubled the energy weight. For the "Sad but Energetic" profile, the only sad song (Empty Porch Light) dropped out of the top 5. The rankings were different, not more accurate, so I reverted the weights.

---

## Design Decisions

- **Agent + validator instead of trusting raw model output.** A language model's reply is text, not guaranteed data. It can add code fences or extra words, invent a genre the catalog doesn't have, or return an energy outside 0–1. Passing that straight to `score_song` could crash the program or silently give meaningless scores. So Gemini only *proposes* a profile, and plain Python code decides whether to accept it. Returning `None` and skipping the profile is safer than guessing.
- **Giving Gemini the allowed-word lists.** The prompt includes the full `Genres` and `Moods` lists and asks Gemini to use only those words. A genre or mood outside the catalog's vocabulary could never earn genre or mood points, so the profile would be useless. Giving the lists up front makes a valid answer more likely, and the validator still checks it in case Gemini ignores the instruction.
- **The "Unknown Genre" trade-off.** For `{"genre": "classical", "mood": "chill", "energy": 0.2}`, the top-scored song was Moonlit Sonata Sketch, the only genre match. The agent instead picked Spacewalk Thoughts, a mood match from a different genre. That is not clearly better: someone who asked for classical might prefer the classical song even if its mood is off. The agent's rule simply puts mood first, and this is one case where that choice is debatable.
- **Mood-first check vs. the existing genre bias.** The scoring rule gives genre +2.0 but mood only +1.0, so genre usually wins (see *Expected Bias*). `pick_best` deliberately leans the other way and puts mood first, but only within the top 5. It does not change any score. It acts as a second opinion that catches cases like "Sad but Energetic", where the scorer recommends a happy song to someone who asked for sad. It doesn't remove the genre bias; it partly offsets it at the final step.

---

## Limitations and Risks

The catalog is small and has only one rock song. The system favors genre over mood. It does not understand lyrics or language.

In addition, for the agent:

- The "From Sentence" profile depends on Gemini, which is not fully deterministic, so the same sentence can give different recommendations on different runs.
- The agent needs a network connection and a valid API key. If the API call itself fails, `sentence_to_profile` does not catch that error, so the program will stop. Only bad *replies* are handled.
- `pick_best` only looks inside the top 5. If no song with the right mood makes the top 5, it falls back to the top-scored song.

---

## Reflection

Adding the agent showed me that the hard part of using an LLM in a program is not calling it but deciding what to do when its answer is wrong, empty, or slightly off-format. A real failure (the `python`-labeled code fence) taught me more about validation than the happy path did. The full responsible-AI reflection, including bias and limitations, is in the Personal Reflection section of the [Model Card](model_card.md).
