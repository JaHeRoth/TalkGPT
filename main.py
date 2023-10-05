import shutil
from pathlib import Path

from chat_bot import ChatBot, OpenAIResponder, HuggingFaceResponder
from logger import Logger, Verbosity
from recorder import Recorder
from speaker import Speaker
from transcriber import Transcriber


# TODO?: Refactor (maybe LangChain can help reduce messiness)
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


tmpdir = Path(".tmp/")
tmpfile = tmpdir / "audio.mp3"
responder = HuggingFaceResponder()
logger = Logger(verbosity=Verbosity.NORMAL)
recorder = Recorder(logger)
transcriber = Transcriber(responder=None)
speaker = Speaker(logger)
print("What kind of chatbot should I be? Please write your answer and press Enter:")
bot = ChatBot(responder, system_message=input())
while True:
    setup_dir(tmpdir)
    recorder.record(tmpfile)
    prompt = transcriber.transcribe(tmpfile, bot.messages)
    logger.priority_log(f"You: {prompt}")
    response = bot.respond(prompt)
    logger.priority_log(f"Bot: {response}")
    speaker.speak(response, tmpfile)
