"""Tiny HTTP-ish front end with per-client rate limiting."""


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


class RateLimiter:
    """One TokenBucket per client id."""

    def __init__(self, capacity, rate):
        self.capacity = capacity
        self.rate = rate
        self.buckets = {}
        self.allowed = 0
        self.denied = 0

    def allow(self, client_id, now):
        bucket = self.buckets.get(client_id)
        if bucket is None:
            bucket = self.buckets[client_id] = TokenBucket(self.capacity, self.rate, now)
        ok = bucket.allow(now)
        if ok:
            self.allowed += 1
        else:
            self.denied += 1
        return ok

    def stats(self):
        return {"allowed": self.allowed, "denied": self.denied, "clients": len(self.buckets)}


def handle_request(limiter, client_id, path, now):
    if not limiter.allow(client_id, now):
        return 429, "slow down"
    if path == "/health":
        return 200, "ok"
    return 404, "not found"
