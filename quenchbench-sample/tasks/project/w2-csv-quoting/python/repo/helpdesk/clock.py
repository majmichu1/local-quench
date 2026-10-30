class ManualClock:
    """A clock that only moves when told to. The helpdesk never reads the system time."""

    def __init__(self, start=0):
        self._now = start

    def now(self):
        return self._now

    def advance(self, minutes):
        self._now += minutes
        return self._now

    def set(self, minutes):
        self._now = minutes
