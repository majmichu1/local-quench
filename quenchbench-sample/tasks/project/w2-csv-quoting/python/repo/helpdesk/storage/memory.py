from ..errors import TicketNotFound


class MemoryStore:
    """Tickets and users, kept in memory. Tickets are stored by reference, not copied."""

    def __init__(self):
        self._tickets = {}
        self._users = {}
        self._next = 1

    def next_id(self):
        n = self._next
        self._next += 1
        return n

    def put(self, ticket):
        self._tickets[ticket.id] = ticket

    def get(self, ticket_id):
        try:
            return self._tickets[ticket_id]
        except KeyError:
            raise TicketNotFound(ticket_id) from None

    def all(self):
        return [self._tickets[i] for i in sorted(self._tickets)]

    def add_user(self, user):
        self._users[user.name] = user

    def user(self, name):
        return self._users.get(name)

    def agents(self):
        return sorted((u for u in self._users.values() if u.role == "agent"), key=lambda u: u.name)
