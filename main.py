import shutil
from pathlib import Path

import openai
import sounddevice as sd
import soundfile as sf
from gtts import gTTS

from chat_bot import ChatBot
from logger import Logger, Verbosity
from recorder import Recorder
from transcriber import Transcriber


# TODO: Write README and LICENSE
# TODO?: Handle long recordings (split of new file every 30 seconds or so, launching async transcribing,
#  before combining everything at the end)
#  https://platform.openai.com/docs/guides/speech-to-text/longer-inputs
# TODO: Support adding PDFs to context
# TODO?: Streamlit
# TODO?: Improve text to speech
# TODO?: Generate avatars from speech (to make it as if you're talking to a person)


def setup_dir(dirpath: Path):
    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath.mkdir()


def speak(text: str, fname):
    tts = gTTS(text=text, lang='en')

    tts.save(fname)
    data, fs = sf.read(fname, dtype='float32')
    sd.play(data, fs)
    sd.wait()
    logger.log("Done speaking")


tmpdir = Path(".tmp/")
tmpfile = tmpdir / "audio.mp3"
logger = Logger(verbosity=Verbosity.NORMAL)
recorder = Recorder(logger)
transcriber = Transcriber(run_locally=False)
print("What kind of chatbot should I be? Please write your answer and press Enter:")
bot = ChatBot(system_message=input(), run_locally=False)
while True:
    setup_dir(tmpdir)
    recorder.record(tmpfile)
    prompt = transcriber.transcribe(tmpfile, bot.messages)
    logger.priority_log(f"You: {prompt}")
    response = bot.respond(prompt)
    logger.priority_log(f"Bot: {response}")
    speak(response, tmpfile)
