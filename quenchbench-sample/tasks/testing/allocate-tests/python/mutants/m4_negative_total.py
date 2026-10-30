def allocate(total, weights):
    """Split `total` (integer cents) into parts proportional to `weights` (largest remainder method)."""
    if not weights or any(w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError("weights must be non-negative and not all zero")
    s = sum(weights)
    shares = [total * w // s for w in weights]
    rems = [(total * w % s, -i) for i, w in enumerate(weights)]
    left = total - sum(shares)
    for _, neg_i in sorted(rems, reverse=True)[:left]:
        shares[-neg_i] += 1
    return shares
