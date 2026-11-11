# chatbot.py
# Author: Pamela Emmrich

HANDOFF_WORDS = ["payment", "card"]
MAX_TOOL_ROUNDS = 3


class SupportChatbot:
    """A support chatbot. The model decides. The toolbox checks every tool request."""

    def __init__(self, name, instructions, tools, model):
        """Set up one chatbot with its own name, instructions, tools, model, and history."""
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.model = model
        self.history = []

    def respond(self, user_message):
        """Record the user's message, choose a reply, record it, and return it."""
        self.history.append({"role": "user", "content": user_message})
        reply = self.choose_reply(user_message)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def choose_reply(self, user_message):
        """Pass payment questions to a person. Send everything else to the model."""
        if self.needs_human(user_message.lower()):
            return "I can't help with that here. I'm passing you to a human agent."
        return self.model_reply()

    def needs_human(self, text):
        """Return True if the message is about something a person must handle."""
        for word in HANDOFF_WORDS:
            if word in text:
                return True
        return False

    def model_reply(self):
        """Ask the model. Run each tool it asks for, then ask again, up to a limit."""
        rounds = 0
        while rounds < MAX_TOOL_ROUNDS:
            tool_list = self.tools.tool_list()
            decision = self.model.decide(self.instructions, self.history, tool_list)
            if decision is None:
                return "Sorry, I can't answer that right now. Please try again in a moment."
            if "text" in decision:
                return decision["text"]
            name = decision["tool"]
            arguments = decision["arguments"]
            result = self.tools.run(name, arguments, self.history)
            self.history.append(
                {
                    "role": "tool",
                    "tool_name": name,
                    "arguments": arguments,
                    "content": result,
                }
            )
            rounds += 1
        return "Sorry, I couldn't finish that. I'm passing you to a human agent."

    def count_user_messages(self):
        """Return how many messages the user has sent so far."""
        count = 0
        for message in self.history:
            if message["role"] == "user":
                count += 1
        return count