import argparse
import random
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from bengalistoryteller import story_store
from bengalistoryteller.tts_mms import BengaliTTS

load_dotenv()

PROMPT = """
Write a short Bengali horror story for children about a king and a queen,
in 5-6 lines. Make it spooky but not too frightening, with a gentle ending.

Use these ingredients:
- Setting: {setting}
- Spooky thing: {creature}
- Twist: {twist}
- Lesson at the end: {lesson}

Give the king and queen fresh names and do not start with "এক পুরনো রাজপ্রাসাদে".
{avoid}
Use natural Bengali script only (no English words, no numbers, no markdown).
End each sentence with । ! or ?. Return only the story.
"""

# One item from each list is picked at random for every new story.
SETTINGS = [
    "a palace on a misty river island",
    "a royal boat on a stormy night",
    "a hunting camp deep in the Sundarbans",
    "a forgotten palace library",
    "a royal garden under a red moon",
    "a mountain fort covered in snow",
    "the palace kitchen at midnight",
    "an abandoned temple near the kingdom border",
]
CREATURES = [
    "a mischievous Mechho Bhoot who steals fish",
    "a talking owl with glowing eyes",
    "a Brahmadaitya living in a banyan tree",
    "a Shakchunni wearing the queen's bangles",
    "a portrait whose eyes follow people",
    "footprints that appear in the dust by themselves",
    "a Skondhokata (headless ghost) looking for his head",
    "a lost little Petni who cries at night",
]
TWISTS = [
    "the ghost is actually afraid of the king",
    "the spooky sound turns out to be a hungry animal",
    "the queen bravely solves the mystery alone",
    "the ghost needs help to find something it lost",
    "the young prince or princess is the one who is not scared",
    "the ghost only wants to be invited to a feast",
]
LESSONS = [
    "be kind even to those who look scary",
    "courage means facing fear calmly",
    "do not judge anyone by appearance",
    "sharing makes everyone happy",
    "always tell the truth",
]

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-lite-latest"]
RETRIES_PER_MODEL = 2


def build_prompt():
    theme = {
        "setting": random.choice(SETTINGS),
        "creature": random.choice(CREATURES),
        "twist": random.choice(TWISTS),
        "lesson": random.choice(LESSONS),
    }
    recent = story_store.load_stories()[-5:]
    avoid = ""
    if recent:
        openings = "\n".join(f"- {s['text'].split('।')[0]}" for s in recent)
        avoid = f"These stories already exist; do not repeat their plot or opening:\n{openings}\n"
    return PROMPT.format(avoid=avoid, **theme), theme


MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-lite-latest"]
RETRIES_PER_MODEL = 2


def generate_story(prompt):
    client = genai.Client(
        http_options=types.HttpOptions(
            timeout=60_000, retry_options=types.HttpRetryOptions(attempts=1)
        )
    )
    last_error = None
    for model in MODELS:
        for attempt in range(1, RETRIES_PER_MODEL + 1):
            print(f"Asking {model} (try {attempt})...", flush=True)
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=1.2),
                )
                if response.text:
                    return response.text, model
                last_error = "empty response"
            except errors.APIError as e:
                last_error = f"{e.code} {e.message}"
                print(f"  failed: {last_error}", flush=True)
                if e.code not in (429, 500, 503, 504):
                    break  # not a temporary problem, try next model
            time.sleep(2 * attempt)
    raise SystemExit(f"Could not get a story from Gemini: {last_error}")


def speak(story):
    out_path = story_store.audio_path_for(story["id"])
    synth = BengaliTTS()
    wav = synth.tts(story["text"])
    synth.save_wav(wav, out_path)
    story_store.set_audio(story["id"], out_path)
    print(f"Done! Saved {out_path}")


def list_stories():
    stories = story_store.load_stories()
    if not stories:
        print("No stories saved yet.")
    for s in stories:
        first_line = s["text"].strip().splitlines()[0]
        print(f"[{s['id']}] {s['created_at']}  {first_line}")


def main():
    parser = argparse.ArgumentParser(description="Bengali story teller")
    parser.add_argument("--id", type=int, help="replay a saved story by id (no LLM call)")
    parser.add_argument("--list", action="store_true", help="list saved stories")
    args = parser.parse_args()

    if args.list:
        list_stories()
        return

    if args.id is not None:
        story = story_store.get_story(args.id)
        if story is None:
            print(f"No story with id {args.id}. Use --list to see saved ids.")
            return
        print(f"Replaying story {story['id']} from {story_store.STORE_FILE}")
    else:
        prompt, theme = build_prompt()
        print(f"Theme: {theme}")
        text, model = generate_story(prompt)
        story = story_store.add_story(text, model=model, theme=theme)
        print(f"Saved new story with id {story['id']}")

    print(story["text"])
    speak(story)


if __name__ == "__main__":
    main()
