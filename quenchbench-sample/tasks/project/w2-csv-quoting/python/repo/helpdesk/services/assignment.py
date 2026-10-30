from ..config import ACTIVE


class Assigner:
    """Picks an agent for a ticket: skilled agents first, then the least loaded one."""

    def __init__(self, store):
        self.store = store

    def load(self, agent):
        return sum(1 for t in self.store.all() if t.assignee == agent.name and t.status in ACTIVE)

    def pick(self, ticket):
        agents = self.store.agents()
        if not agents:
            return ""
        wanted = set(ticket.tags)
        pool = [a for a in agents if wanted & set(a.skills)] or agents
        best = min(pool, key=lambda a: (self.load(a), a.name))
        return best.name
