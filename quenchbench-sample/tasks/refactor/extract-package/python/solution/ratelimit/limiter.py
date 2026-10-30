from ratelimit.bucket import TokenBucket


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
