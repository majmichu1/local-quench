from dataclasses import dataclass, field

from ..config import ACTIVE


@dataclass
class Event:
    time: int
    kind: str
    detail: str = ""


@dataclass
class Comment:
    author: str
    text: str
    public: bool
    time: int


@dataclass
class Ticket:
    id: int
    title: str
    requester: str
    priority: str
    created: int
    due: int
    status: str = "new"
    assignee: str = ""
    tags: list = field(default_factory=list)
    updated: int = 0
    first_response: int = -1
    resolved_at: int = -1
    comments: list = field(default_factory=list)
    history: list = field(default_factory=list)

    def is_active(self):
        return self.status in ACTIVE

    def log(self, time, kind, detail=""):
        self.history.append(Event(time, kind, detail))
        self.updated = time
