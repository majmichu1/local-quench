from collections import deque


def _check(k):
    if k < 1:
        raise ValueError("window size must be >= 1")


def _rolling(values, k, better):
    _check(k)
    out, dq = [], deque()
    for i, v in enumerate(values):
        while dq and not better(values[dq[-1]], v):
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(values[dq[0]])
    return out


def rolling_max(values, k):
    """Max of every full window of k consecutive values."""
    return _rolling(values, k, lambda a, b: a > b)


def rolling_min(values, k):
    """Min of every full window of k consecutive values."""
    return _rolling(values, k, lambda a, b: a < b)
