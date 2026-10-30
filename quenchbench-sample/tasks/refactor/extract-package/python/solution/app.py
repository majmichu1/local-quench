"""Tiny HTTP-ish front end with per-client rate limiting."""
from ratelimit import RateLimiter, TokenBucket

__all__ = ["RateLimiter", "TokenBucket", "handle_request"]


def handle_request(limiter, client_id, path, now):
    if not limiter.allow(client_id, now):
        return 429, "slow down"
    if path == "/health":
        return 200, "ok"
    return 404, "not found"
