import openai


class Transcriber:
    def transcribe(self, fpath, messages: list[dict]):
        return self.post_process(self.initial_transcribe(fpath, messages), messages)

    def initial_transcribe(self, fpath, messages: list[dict]):
        # This prompt is fed to Whisper. Whisper will then try to match its style. Whisper ignores all but the
        # last 244 tokens, which is why the most important prompts are at the end.
        input_prompt = "\n".join(
            [message["content"] for message in messages[1:-1]]
            # All but the system message and the last assistant message
        ) + (
                messages[0]["content"] + "\n" +  # The system message
                messages[-1]["content"] + "\n" +  # The assistant's last message
                "Hello, welcome to my lecture.\n" +  # To include punctuation
                "Umm, let me think like, hmm... Okay, here's what I'm, like, thinking."  # To include filler words
                # TODO: Also include last words of the last part of transcription, if split into multiple files
        )
        with open(fpath, "rb") as f:
            return openai.Audio.transcribe("whisper-1", f, prompt=input_prompt, language="en")["text"]

    def post_process(self, raw_transcription, messages: list[dict]):
        # Post-processing with GPT-4
        post_processing_system = "You are a helpful assistant. Your task is to correct any spelling discrepancies in " \
                                 "the transcribed text. Only add necessary punctuation such as periods, commas, and " \
                                 "capitalization, and use only the context provided."
        post_processing_messages = (
                [{"role": "system", "content": post_processing_system}]
                + messages[1:]
                + [{"role": "user", "content": raw_transcription}]
        )
        return openai.ChatCompletion.create(
            model="gpt-4", messages=post_processing_messages
        )["choices"][0]["message"]["content"]
