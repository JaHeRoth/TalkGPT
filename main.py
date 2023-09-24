import shutil
from pathlib import Path

import openai
import sounddevice as sd
import soundfile as sf
from gtts import gTTS

from recorder import Recorder

# TODO: Write README and LICENSE
# TODO: Handle long recordings (either during recording or transcription)
#  https://platform.openai.com/docs/guides/speech-to-text/longer-inputs
# TODO: Optimize transcriptions:
#  https://platform.openai.com/docs/guides/speech-to-text/prompting
#  https://platform.openai.com/docs/guides/speech-to-text/improving-reliability
# TODO: Support adding PDFs to context
# TODO?: Improve text to speech
# TODO?: Generate avatars from speech (to make it as if you're talking to a person)


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
