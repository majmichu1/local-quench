def overdue(tickets, now):
    """Active tickets whose due time has passed, most overdue first (ties by id)."""
    late = [t for t in tickets if t.is_active() and t.due < now]
    return sorted(late, key=lambda t: (t.due, t.id))
