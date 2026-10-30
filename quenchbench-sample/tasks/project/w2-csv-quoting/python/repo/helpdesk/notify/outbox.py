from dataclasses import dataclass

from .templates import render


@dataclass
class Message:
    to: str
    text: str
    time: int


class Outbox:
    """Collects the messages the helpdesk wants to send. Nothing leaves the process."""

    def __init__(self):
        self.messages = []

    def send(self, to, key, time, **values):
        if not to:
            return
        self.messages.append(Message(to, render(key, **values), time))

    def for_user(self, name):
        return [m for m in self.messages if m.to == name]
