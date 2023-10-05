import openai


class ChatBot:
    def __init__(self, run_locally, system_message: str):
        self.run_locally = run_locally
        self.messages = [{"role": "system", "content": system_message}]

    def respond(self, message: str):
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(model="gpt-4", messages=self.messages)["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": response})
        return response
