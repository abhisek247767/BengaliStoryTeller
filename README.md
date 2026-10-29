# Bengali Story Teller

## The idea

You come home tired after a long day at work, and your child asks, "Tell me a story!"
Most nights you're too tired to make up something new, and the same old stories
get boring.

Bengali Story Teller fixes that. Run one command and it:

1. **Writes a fresh story.** Gemini writes a short, gently spooky Bengali story about
   a king and a queen. Each story gets a random setting, ghost, twist and lesson,
   so no two nights are the same.
2. **Reads it aloud.** A Bengali voice model running on your own computer turns the
   story into an audio file you can play for your child.
3. **Saves it.** Every story is saved with an id (1, 2, 3…). When your child wants
   their favourite one again, replay it without asking Gemini for a new story.

The stories are scary enough to be fun, and every one has a kind ending and a small
lesson.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Get a Gemini API key from https://aistudio.google.com/apikey.
3. Create a `.env` file in the project folder:
   ```
   GEMINI_API_KEY=your-key-here
   ```

The first run installs the dependencies and downloads the Bengali voice model
(`facebook/mms-tts-ben`), so it takes a little longer.

## How to run

```bash
uv run bengalistoryteller            # create a new story and read it aloud
uv run bengalistoryteller --list     # list all saved stories with their ids
uv run bengalistoryteller --id 1     # read saved story 1 again (no Gemini call)
```

Stories are saved in `stories/stories.json` and the audio in `stories/story_<id>.wav`.

## 📖 For Better Understanding

For a detailed explanation of this project, its architecture, implementation, and how it works, check out my Dev.to article:

👉 [Built a Local AI Code Reviewer with Ollama — Private & Open Source](https://dev.to/abhisekroy169/bengalistoryteller-a-free-offline-ai-that-reads-bengali-bedtime-stories-jpl)

<p align="center">
  <img alt="Sloan, the sloth mascot" width="250px" src="https://thepracticaldev.s3.amazonaws.com/uploads/user/profile_image/31047/af153cd6-9994-4a68-83f4-8ddf3e13f0bf.jpg">
  <br>
  <strong>Happy Learning</strong> ❤️
</p>


