def matches(ticket, term):
    if term.field == "text":
        hit = term.value in ticket.title.lower()
    elif term.field == "tag":
        hit = term.value in [x.lower() for x in ticket.tags]
    else:
        hit = getattr(ticket, term.field).lower() == term.value
    return hit != term.negated


def run(tickets, terms):
    return [t for t in tickets if all(matches(t, term) for term in terms)]
