class TokenBucket:
    """Holds up to `capacity` tokens, refilled at `rate` tokens per second."""

    def __init__(self, capacity, rate, now=0.0):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity = capacity
        self.rate = rate
        self.tokens = float(capacity)
        self.last = now

    def allow(self, now):
        elapsed = max(0.0, now - self.last)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last = max(self.last, now)
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
