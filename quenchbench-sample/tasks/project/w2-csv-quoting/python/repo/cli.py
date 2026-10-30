"""Tiny demo: python3 cli.py prints a report for a few sample tickets."""
from helpdesk import Helpdesk

hd = Helpdesk()
hd.add_agent("ana", ["network"])
hd.add_agent("ben")
hd.add_requester("zoe")
for title, prio, tags in [("VPN drops every hour", "high", ["vpn"]), ("Printer jammed", "low", []),
                          ("Cannot log in", "urgent", ["sso"])]:
    t = hd.tickets.create(title, "zoe", prio, tags)
    hd.tickets.auto_assign(t.id)
print(hd.report())
