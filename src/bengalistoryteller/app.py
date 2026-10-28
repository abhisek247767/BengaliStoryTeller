import argparse

from dotenv import load_dotenv
from google import genai

from bengalistoryteller import story_store
from bengalistoryteller.tts_mms import BengaliTTS

load_dotenv()

PROMPT = """
Write a short Bengali horror story for children about a king and a queen,
in 5-6 lines. Make it spooky but not too frightening, with a gentle ending.
Use natural Bengali script only (no English words, no numbers, no markdown).
End each sentence with । ! or ?. Return only the story.
"""


def generate_story():
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=PROMPT,
    )
    return response.text


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
        story = story_store.add_story(generate_story())
        print(f"Saved new story with id {story['id']}")

    print(story["text"])
    speak(story)


if __name__ == "__main__":
    main()
