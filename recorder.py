import asyncio
import queue
import sys

import sounddevice as sd
import soundfile as sf

from logger import Logger


class Recorder:
    def __init__(self, logger: Logger, sample_rate=44100, channels=2):
        self.logger = logger
        self.sample_rate = sample_rate
        self.channels = channels
        self.q = queue.Queue()
        self.stop_recording = None
        self.recording_stopped = None

    async def _wait_for_input(self):
        self.logger.log("waiting for input")
        input()  # Wait for the user to press Enter
        self.logger.log("received input")
        self.stop_recording.set()  # Set the stop_event

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    async def _capture_mic_input(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self._callback):
            self.logger.priority_log('Now recording. Press Enter to stop recording')
            await self.stop_recording.wait()  # Wait until the stop_event is set
        self.logger.log("Done recording")
        self.recording_stopped.set()  # Set the recording_stopped event

    async def _persist_captured(self, file_path):
        with sf.SoundFile(file_path, mode='x', samplerate=self.sample_rate, channels=self.channels) as file:
            while not self.recording_stopped.is_set() or not self.q.empty():
                if not self.q.empty():
                    file.write(self.q.get())
                else:
                    await asyncio.sleep(0.1)

    async def _async_record(self, file_path):
        self.stop_recording = asyncio.Event()
        self.recording_stopped = asyncio.Event()
        self.logger.priority_log("Press Enter to start recording your response.")
        input()
        record_task = asyncio.create_task(self._capture_mic_input())
        write_task = asyncio.create_task(self._persist_captured(file_path))
        input_task = asyncio.create_task(self._wait_for_input())
        await input_task
        await record_task
        await write_task

    def record(self, file_path):
        asyncio.run(self._async_record(file_path))
