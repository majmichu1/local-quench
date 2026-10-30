from .rolling import rolling_max, rolling_min


def windows_over(values, k, threshold):
    """Start indexes of the windows whose maximum is above threshold."""
    return [i for i, m in enumerate(rolling_max(values, k)) if m > threshold]


def spread(values, k):
    """max - min for every window."""
    return [hi - lo for hi, lo in zip(rolling_max(values, k), rolling_min(values, k))]
