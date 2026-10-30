import unittest

from helpdesk import Helpdesk

HEADER = "id,title,requester,priority,status,assignee,tags,created,due\n"


def desk():
    hd = Helpdesk()
    hd.add_agent("Lee, Sam")
    hd.add_agent("ana")
    hd.add_requester("zoe")
    return hd


class CsvQuoting(unittest.TestCase):
    def test_plain_rows_are_unchanged(self):
        hd = desk()
        hd.tickets.create("Printer jammed", "zoe", "high", ["hw", "office"])
        self.assertEqual(hd.export_csv(), HEADER + "1,Printer jammed,zoe,high,new,,hw;office,0,480\n")

    def test_every_column_is_quoted_when_needed(self):
        hd = desk()
        a = hd.tickets.create('Printer, "HP" jammed', "Doe, Jane", "normal", ["a,b", "x"])
        hd.tickets.assign(a.id, "Lee, Sam")
        hd.tickets.create("Line one\nline two", "zoe", "high")
        hd.tickets.create('say "hi"', "zoe", "low", ["it's fine"])
        hd.tickets.create("tab\there; semi", "zoe", "urgent")
        hd.tickets.create("win\r\nline", "zoe", "urgent")
        want = (HEADER
                + '1,"Printer, ""HP"" jammed","Doe, Jane",normal,new,"Lee, Sam","a,b;x",0,1440\n'
                + '2,"Line one\nline two",zoe,high,new,,,0,480\n'
                + '3,"say ""hi""",zoe,low,new,,it\'s fine,0,4320\n'
                + "4,tab\there; semi,zoe,urgent,new,,,0,120\n"
                + '5,"win\r\nline",zoe,urgent,new,,,0,120\n')
        self.assertEqual(hd.export_csv(), want)

    def test_import_gets_the_same_tickets_back(self):
        hd = desk()
        hd.tickets.create('Printer, "HP" jammed', "Doe, Jane", "normal", ["a,b", "x"])
        hd.tickets.create("Line one\nline two", "zoe", "high")
        text = hd.export_csv()
        other = desk()
        made = other.import_csv(text)
        self.assertEqual([t.title for t in made], ['Printer, "HP" jammed', "Line one\nline two"])
        self.assertEqual([t.requester for t in made], ["Doe, Jane", "zoe"])
        self.assertEqual(made[0].tags, ["a,b", "x"])
        self.assertEqual(other.export_csv().replace("\n2,", "\n2,"), text)


if __name__ == "__main__":
    unittest.main()
