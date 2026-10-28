import re
import numpy as np
import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

MODEL = "facebook/mms-tts-ben"
PAUSE_SECONDS = 0.6     # pause after each ।
SPEED = 0.9             # 1.0 = normal, lower = slower (good for stories)

model = VitsModel.from_pretrained(MODEL)
tok = AutoTokenizer.from_pretrained(MODEL)
model.speaking_rate = SPEED
torch.manual_seed(42)   # same voice style on every run

text = """এক রাতে রাহুল একা ঘরে ঘুমাচ্ছিল।
হঠাৎ জানালার বাইরে থেকে কেউ তার নাম ধরে ডাকল।
সে জানালা খুলে দেখল, বাইরে কেউ নেই।
ঠিক তখনই তার পিছন থেকে একটা ঠান্ডা হাত তার কাঁধে পড়ল।
ভয়ে সে পিছনে তাকাতেই দেখল, আয়নায় তার প্রতিবিম্ব হাসছে, কিন্তু সে নিজে হাসছে না।
তারপর আয়নার ভিতর থেকে একটা কণ্ঠ বলল, "এবার তোমার পালা!" """

# Clean: remove quotes/brackets, English letters, digits
text = re.sub(r'["“”\'‘’()\[\]{}A-Za-z0-9]', '', text)
text = re.sub(r"\s+", " ", text).strip()

# Split at । ! ?
sentences = [s.strip() for s in re.split(r"(?<=[।!?])\s*", text) if s.strip()]

sr = model.config.sampling_rate
silence = np.zeros(int(sr * PAUSE_SECONDS), dtype=np.float32)

audio = []
for i, s in enumerate(sentences, 1):
    print(f"[{i}/{len(sentences)}] {s}")
    inputs = tok(s, return_tensors="pt")
    with torch.no_grad():
        wav = model(**inputs).waveform.squeeze().numpy()
    audio.extend([wav, silence])

sf.write("out_mms.wav", np.concatenate(audio), sr)
print("Done! Saved out_mms.wav")