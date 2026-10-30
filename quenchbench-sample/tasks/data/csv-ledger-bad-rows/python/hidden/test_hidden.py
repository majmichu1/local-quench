import unittest

from ledger import parse_ledger
from report import balances

TEXT = ("date,account,amount,memo\r\n" "2026-01-02,Cash,12,coffee\r\n" "2026-01-03, Bank ,-3.50,\"rent, january\"\n" "\n" "2026-01-04,Bank,10.00,\"multi\nline \"\"memo\"\"\"\n" "2026-01-05,Cash,1.5,bad cents\n" "2026-1-06,Cash,1.00,bad date\n" "2026-01-07,   ,1.00,no account\n" "2026-01-08,Cash,1.00\n" "2026-01-09,Cash,1.00,x,extra\n" "2026-01-10,Cash,+1.00,plus\n" "2026-01-11,Cash,-0.05,te\"st\n" "2026-01-12,Cash,7,\"\"\n" "2026-01-13,Cash,1,\"never closed\nstill open")


class T(unittest.TestCase):
    def test_full(self):
        rows, errors = parse_ledger(TEXT)
        self.assertEqual(rows, [
            {"date": "2026-01-02", "account": "Cash", "amount_cents": 1200, "memo": "coffee"},
            {"date": "2026-01-03", "account": "Bank", "amount_cents": -350, "memo": "rent, january"},
            {"date": "2026-01-04", "account": "Bank", "amount_cents": 1000, "memo": 'multi\nline "memo"'},
            {"date": "2026-01-11", "account": "Cash", "amount_cents": -5, "memo": 'te"st'},
            {"date": "2026-01-12", "account": "Cash", "amount_cents": 700, "memo": ""},
        ])
        self.assertEqual(errors, [(7, "bad amount"), (8, "bad date"), (9, "empty account"), (10, "field count"),
                                  (11, "field count"), (12, "bad amount"), (15, "unterminated quote")])
        self.assertEqual(balances(rows), {"Cash": 1895, "Bank": 650})

    def test_header_only_and_no_trailing_newline(self):
        self.assertEqual(parse_ledger("date,account,amount,memo"), ([], []))
        self.assertEqual(parse_ledger("h\n2026-02-01,A,0.10,m"),
                         ([{"date": "2026-02-01", "account": "A", "amount_cents": 10, "memo": "m"}], []))

    def test_no_csv_module(self):
        self.assertNotIn("import csv", open("ledger.py").read())
