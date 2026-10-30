from app import RateLimiter


def deny_ratio(limiter: RateLimiter) -> float:
    s = limiter.stats()
    total = s["allowed"] + s["denied"]
    return round(s["denied"] / total, 3) if total else 0.0
