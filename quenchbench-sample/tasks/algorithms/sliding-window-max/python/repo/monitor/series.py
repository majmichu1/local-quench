def load(text):
    """One number per line; blank lines are skipped."""
    return [float(line) for line in text.splitlines() if line.strip()]
