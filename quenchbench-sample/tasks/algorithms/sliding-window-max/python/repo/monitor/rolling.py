def _check(k):
    if k < 1:
        raise ValueError("window size must be >= 1")


def rolling_max(values, k):
    """Max of every full window of k consecutive values."""
    _check(k)
    return [max(values[i:i + k]) for i in range(len(values) - k + 1)]


def rolling_min(values, k):
    """Min of every full window of k consecutive values."""
    _check(k)
    return [min(values[i:i + k]) for i in range(len(values) - k + 1)]
