import asyncio
import shutil
from pathlib import Path

import sounddevice as sd
import openai
import soundfile as sf

from gtts import gTTS

from recorder import Recorder


def setup_dir(dirpath: Path):
    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath.mkdir()


def transcribe(fname):
    with open(fname, "rb") as f:
        return openai.Audio.transcribe("whisper-1", f)["text"]


def speak(text: str, fname):
    tts = gTTS(text=text, lang='en')

    tts.save(fname)
    data, fs = sf.read(fname, dtype='float32')
    sd.play(data, fs)
    sd.wait()
    print("Done speaking")


print("What kind of chatbot should I be? Please write your answer and press Enter:")
messages = [{
    "role": "system",
    "content": input()
}]
tmpdir = Path(".tmp/")
tmpfile = tmpdir / "audio.wav"
recorder = Recorder()
while True:
    setup_dir(tmpdir)
    recorder.record(tmpfile)
    prompt = transcribe(tmpfile)
    print(f"You: {prompt}")
    print('#' * 80)
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": response})
    print(f"Bot: {response}")
    speak(response, tmpfile)
