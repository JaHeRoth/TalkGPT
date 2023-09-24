import asyncio
import queue
import sys

import sounddevice as sd
import soundfile as sf


class Recorder:
    sample_rate = 44100
    channels = 2
    q = queue.Queue()
    stop_recording = None
    recording_stopped = None

    async def _wait_for_input(self):
        print("waiting for input")
        input()  # Wait for the user to press Enter
        print("received input")
        self.stop_recording.set()  # Set the stop_event

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    async def _record_audio(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self._callback):
            print('#' * 80)
            print('Now recording. Press Enter to stop recording')
            print('#' * 80)
            await self.stop_recording.wait()  # Wait until the stop_event is set
        print("Done recording")
        self.recording_stopped.set()  # Set the recording_stopped event

    async def _write_to_file(self, file):
        while not self.recording_stopped.is_set() or not self.q.empty():
            if not self.q.empty():
                file.write(self.q.get())
            else:
                await asyncio.sleep(0.1)

    async def _async_record(self, file_path):
        print('#' * 80)
        print("Press Enter to start recording your response.")
        input()
        with sf.SoundFile(file_path, mode='x', samplerate=self.sample_rate, channels=self.channels) as file:
            self.stop_recording = asyncio.Event()
            self.recording_stopped = asyncio.Event()
            record_task = asyncio.create_task(self._record_audio())
            write_task = asyncio.create_task(self._write_to_file(file))
            input_task = asyncio.create_task(self._wait_for_input())
            await input_task
            await record_task
            await write_task

    def record(self, file_path):
        asyncio.run(self._async_record(file_path))