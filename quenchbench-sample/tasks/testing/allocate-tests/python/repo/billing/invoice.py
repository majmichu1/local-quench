from billing.allocate import allocate


def split_bill(total_cents, people):
    """people: list of (name, weight). Returns {name: cents}."""
    parts = allocate(total_cents, [w for _, w in people])
    return {name: part for (name, _), part in zip(people, parts)}
