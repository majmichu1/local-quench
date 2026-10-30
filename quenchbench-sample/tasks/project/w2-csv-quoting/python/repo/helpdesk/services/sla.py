from ..config import SLA_MINUTES


class SlaPolicy:
    """Decides when a ticket is due."""

    def __init__(self, minutes=None):
        self.minutes = dict(minutes or SLA_MINUTES)

    def due_for(self, created, priority):
        return created + self.minutes[priority]
