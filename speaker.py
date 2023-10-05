from gtts import gTTS

import sounddevice as sd
import soundfile as sf

from logger import Logger


class Speaker:
    def __init__(self, logger: Logger):
        self.logger = logger

    def speak(self, text: str, fname):
        tts = gTTS(text=text, lang='en')

        tts.save(fname)
        data, fs = sf.read(fname, dtype='float32')
        sd.play(data, fs)
        sd.wait()
        self.logger.log("Done speaking")