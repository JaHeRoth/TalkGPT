import queue
import shutil
from pathlib import Path

import sounddevice as sd
import openai, sys
import soundfile as sf

from gtts import gTTS

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


def setup_dir(dirpath: Path):
    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath.mkdir()


def record(fname):
    with sf.SoundFile(fname, mode='x', samplerate=44100, channels=2) as file:
        print('#' * 80)
        print("Press Enter to start recording your response.")
        input()
        with sd.InputStream(samplerate=44100, channels=2, callback=callback):
            print("Now recording. Press Enter once you are done speaking.")
            print('#' * 80)
            input()  # Wait for the user to press Enter
            while not q.empty():  # Continue writing any remaining data in the queue
                file.write(q.get())


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
while True:
    setup_dir(tmpdir)
    record(tmpfile)
    prompt = transcribe(tmpfile)
    print(f"You: {prompt}")
    print('#' * 80)
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": response})
    print(f"Bot: {response}")
    speak(response, tmpfile)
