TEMPLATES = {
    "created": "Ticket #{id} received: {title}",
    "assigned": "Ticket #{id} assigned to {assignee}: {title}",
    "status": "Ticket #{id} is now {status}: {title}",
    "comment": "New reply on ticket #{id}: {title}",
}


def render(key, **values):
    return TEMPLATES[key].format(**values)
