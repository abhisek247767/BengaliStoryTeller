import re
import numpy as np
import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

MODEL = "facebook/mms-tts-ben"
PAUSE_SECONDS = 0.6     # pause after each ।
SPEED = 0.9             # 1.0 = normal, lower = slower (good for stories)


class BengaliTTS:
    def __init__(self, speed=SPEED, pause_seconds=PAUSE_SECONDS, seed=42):
        self.model = VitsModel.from_pretrained(MODEL)
        self.tok = AutoTokenizer.from_pretrained(MODEL)
        self.model.speaking_rate = speed
        self.pause_seconds = pause_seconds
        self.seed = seed
        self.sr = self.model.config.sampling_rate

    @staticmethod
    def split_sentences(text):
        # Clean: remove quotes/brackets, English letters, digits
        text = re.sub(r'["“”\'‘’()\[\]{}A-Za-z0-9*#_]', '', text)
        text = re.sub(r"\s+", " ", text).strip()
        # Split at । ! ?
        return [s.strip() for s in re.split(r"(?<=[।!?])\s*", text) if s.strip()]

    def tts(self, text):
        torch.manual_seed(self.seed)   # same voice style on every run
        silence = np.zeros(int(self.sr * self.pause_seconds), dtype=np.float32)
        sentences = self.split_sentences(text)

        audio = []
        for i, s in enumerate(sentences, 1):
            print(f"[{i}/{len(sentences)}] {s}")
            inputs = self.tok(s, return_tensors="pt")
            with torch.no_grad():
                wav = self.model(**inputs).waveform.squeeze().numpy()
            audio.extend([wav, silence])
        return np.concatenate(audio)

    def save_wav(self, wav, path):
        sf.write(path, wav, self.sr)
