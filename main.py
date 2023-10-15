import queue
import shutil
import threading

import sounddevice as sd
from pathlib import Path

from chat_bot import ChatBot, OpenAIResponder, HuggingFaceResponder
from logger import Logger, Verbosity
from recorder import Recorder
from speaker import Speaker
from transcriber import Transcriber, OpenAIASR, HuggingFaceASR


# TODO?: Refactor (maybe LangChain can help reduce messiness)
# TODO: Write README and LICENSE
# TODO: Support adding PDFs to context
# TODO?: Streamlit
# TODO: Improve text to speech (support for abritrary Transformers model)
# TODO?: Generate avatars from speech (to make it as if you're talking to a person)


to_be_spoken = queue.Queue()
done_responding = threading.Event()


def setup_dir(dirpath: Path):
    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath.mkdir()


def foo():
    print(f"Bot: ", end="", flush=True)
    for response_segment in bot.respond_stream(prompt):
        if len(response_segment) > 0:
            print(response_segment, end="", flush=True)
            to_be_spoken.put(speaker.speak(response_segment, outfile))
    done_responding.set()
    print()


tmpdir = Path(".tmp/")
infile = tmpdir / "input.mp3"
outfile = tmpdir / "output.mp3"
asr = OpenAIASR()
responder = OpenAIResponder()
logger = Logger(verbosity=Verbosity.NORMAL)
recorder = Recorder(logger)
transcriber = Transcriber(asr, responder=None)
speaker = Speaker(logger)
print("What kind of chatbot should I be? Please write your answer and press Enter:")
bot = ChatBot(responder, system_message=input())
while True:
    setup_dir(tmpdir)
    # # TODO: Multi-threaded transcription for reduced latency (spawn thread already here (or keep one long-living one))
    recorder.record(infile)
    prompt = transcriber.transcribe(infile, bot.messages)
    logger.priority_log(f"You: {prompt}")
    worker = threading.Thread(target=foo)
    worker.start()
    while not done_responding.is_set() or len(to_be_spoken.queue) > 0:
        sd.play(*to_be_spoken.get())
        sd.wait()
    logger.log("Done speaking")
    done_responding.clear()
    # response = bot.respond(prompt)
    # logger.priority_log(f"Bot: {response}")
    # speaker.speak(response, tmpfile)
