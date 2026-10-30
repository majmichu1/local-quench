from .clock import ManualClock
from .exchange.csvio import export_csv, import_tickets
from .models.user import User
from .notify.outbox import Outbox
from .reports.format import render_summary
from .reports.overdue import overdue
from .reports.summary import summarize
from .search.filter import run
from .search.query import parse
from .services.assignment import Assigner
from .services.sla import SlaPolicy
from .services.tickets import TicketService
from .storage.memory import MemoryStore


class Helpdesk:
    """Wires the parts together; this is what the command line and the tests talk to."""

    def __init__(self, clock=None):
        self.clock = clock or ManualClock(0)
        self.store = MemoryStore()
        self.outbox = Outbox()
        self.sla = SlaPolicy()
        self.assigner = Assigner(self.store)
        self.tickets = TicketService(self.store, self.clock, self.outbox, self.sla, self.assigner)

    def add_agent(self, name, skills=(), capacity=5):
        user = User(name, "agent", [s.strip().lower() for s in skills if s.strip()], capacity)
        self.store.add_user(user)
        return user

    def add_requester(self, name):
        user = User(name, "requester")
        self.store.add_user(user)
        return user

    def search(self, text):
        return run(self.store.all(), parse(text))

    def overdue(self):
        return overdue(self.store.all(), self.clock.now())

    def summary(self):
        return summarize(self.store.all())

    def export_csv(self):
        return export_csv(self.store.all())

    def import_csv(self, text):
        return import_tickets(text, self.tickets)

    def report(self):
        return render_summary(self.summary())
