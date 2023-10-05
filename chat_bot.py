from transformers import pipeline, Conversation

import openai


class Responder:
    def __call__(self, messages: list[dict]):
        raise NotImplementedError


class OpenAIResponder(Responder):
    def __init__(self, model_name="gpt-4"):
        self.model_name = model_name

    def __call__(self, messages: list[dict]):
        return openai.ChatCompletion.create(model=self.model_name, messages=messages)["choices"][0]["message"]["content"]


class HuggingFaceResponder(Responder):
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.responder = pipeline("conversational", model_name)

    def __call__(self, messages: list[dict]):
        return self.responder(Conversation(messages.copy())).generated_responses[-1]


class ChatBot:
    def __init__(self, responder: Responder, system_message: str):
        self.messages = [{"role": "system", "content": system_message}]
        self.responder = responder

    def respond(self, message: str):
        self.messages.append({"role": "user", "content": message})
        response = self.responder(self.messages)
        self.messages.append({"role": "assistant", "content": response})
        return response

