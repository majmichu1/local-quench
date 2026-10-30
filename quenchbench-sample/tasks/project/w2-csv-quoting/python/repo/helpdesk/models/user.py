from dataclasses import dataclass, field


@dataclass
class User:
    name: str
    role: str = "agent"  # "agent" or "requester"
    skills: list = field(default_factory=list)
    capacity: int = 5  # how many active tickets an agent should carry
