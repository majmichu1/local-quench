import unittest

from helpdesk import Helpdesk


class SearchReportTests(unittest.TestCase):
    def setUp(self):
        self.hd = hd = Helpdesk()
        hd.add_agent("ana")
        hd.add_requester("zoe")
        self.a = hd.tickets.create("VPN drops", "zoe", "high", ["vpn"])
        self.b = hd.tickets.create("Printer jammed", "zoe", "low")
        hd.tickets.change_status(self.b.id, "open")

    def test_search(self):
        ids = lambda q: [t.id for t in self.hd.search(q)]
        self.assertEqual(ids("status:open"), [2])
        self.assertEqual(ids("tag:vpn"), [1])
        self.assertEqual(ids("-status:open printer"), [])
        self.assertEqual(ids("printer"), [2])

    def test_overdue_and_summary(self):
        self.hd.clock.set(1000)
        self.assertEqual([t.id for t in self.hd.overdue()], [1])
        s = self.hd.summary()
        self.assertEqual(s["status"]["open"], 1)
        self.assertEqual(s["assignee"], {"unassigned": 2})

    def test_csv(self):
        text = self.hd.export_csv()
        self.assertTrue(text.startswith("id,title,requester"))
        made = self.hd.import_csv("title,requester,tags\nBroken mouse,zoe,usb;hw\n")
        self.assertEqual((made[0].title, made[0].tags), ("Broken mouse", ["hw", "usb"]))
