import unittest

from helpdesk import Helpdesk
from helpdesk.errors import InvalidTransition, TicketNotFound, ValidationError


def desk():
    hd = Helpdesk()
    hd.add_agent("ana", ["network"])
    hd.add_agent("ben")
    hd.add_requester("zoe")
    return hd


class TicketTests(unittest.TestCase):
    def test_create_sets_due_from_priority(self):
        hd = desk()
        hd.clock.set(100)
        t = hd.tickets.create("Printer jammed", "zoe", "high")
        self.assertEqual((t.status, t.created, t.due), ("new", 100, 580))
        self.assertEqual(hd.outbox.for_user("zoe")[0].text, "Ticket #1 received: Printer jammed")

    def test_validation(self):
        hd = desk()
        with self.assertRaises(ValidationError):
            hd.tickets.create("  ", "zoe")
        with self.assertRaises(ValidationError):
            hd.tickets.create("x", "zoe", "critical")
        with self.assertRaises(TicketNotFound):
            hd.tickets.get(9)

    def test_status_flow(self):
        hd = desk()
        t = hd.tickets.create("x", "zoe")
        hd.tickets.change_status(t.id, "open")
        hd.tickets.change_status(t.id, "resolved")
        self.assertEqual(t.resolved_at, 0)
        hd.tickets.change_status(t.id, "closed")
        with self.assertRaises(InvalidTransition):
            hd.tickets.change_status(t.id, "open")

    def test_comment_sets_first_response(self):
        hd = desk()
        t = hd.tickets.create("x", "zoe")
        hd.tickets.assign(t.id, "ana")
        hd.clock.advance(30)
        hd.tickets.comment(t.id, "zoe", "hello")
        self.assertEqual(t.first_response, -1)
        hd.tickets.comment(t.id, "ana", "on it")
        self.assertEqual(t.first_response, 30)

    def test_tags_and_auto_assign(self):
        hd = desk()
        t = hd.tickets.create("VPN", "zoe", tags=["Network", " vpn "])
        self.assertEqual(t.tags, ["network", "vpn"])
        self.assertEqual(hd.tickets.auto_assign(t.id), "ana")
