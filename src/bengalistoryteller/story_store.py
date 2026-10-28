import json
from datetime import datetime
from pathlib import Path

STORE_DIR = Path("stories")
STORE_FILE = STORE_DIR / "stories.json"


def load_stories():
    if not STORE_FILE.exists():
        return []
    return json.loads(STORE_FILE.read_text(encoding="utf-8"))


def _write(stories):
    STORE_DIR.mkdir(exist_ok=True)
    STORE_FILE.write_text(
        json.dumps(stories, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_story(text, model=None, theme=None):
    stories = load_stories()
    story = {
        "id": max((s["id"] for s in stories), default=0) + 1,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "theme": theme,
        "text": text,
        "audio": None,
    }
    stories.append(story)
    _write(stories)
    return story


def get_story(story_id):
    for s in load_stories():
        if s["id"] == story_id:
            return s
    return None


def set_audio(story_id, audio_path):
    stories = load_stories()
    for s in stories:
        if s["id"] == story_id:
            s["audio"] = str(audio_path)
    _write(stories)


def audio_path_for(story_id):
    return STORE_DIR / f"story_{story_id}.wav"
