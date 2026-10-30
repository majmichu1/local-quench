import unittest

from forge_ui import Browser


class UITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = Browser()

    @classmethod
    def tearDownClass(cls):
        cls.b.close()

    def open(self, path="index.html", width=1280, height=800):
        page = self.b.open(path, width=width, height=height)
        page.set_default_timeout(3000)
        self.addCleanup(page.close)
        return page

    def texts(self, page, sel):
        return [t.strip() for t in page.locator(sel).all_inner_texts()]

    def focused(self, page):
        return page.evaluate("document.activeElement ? document.activeElement.id : ''")

    def style(self, page, sel, prop):
        return page.evaluate("([s, p]) => getComputedStyle(document.querySelector(s))[p]", [sel, prop])

    def no_errors(self):
        self.assertEqual(self.b.errors, [], "console errors or uncaught exceptions")


import json


class T(UITest):
    def books(self, page):
        out = []
        for i in range(page.locator("#book-list li.book").count()):
            li = page.locator("#book-list li.book").nth(i)
            out.append((li.locator(".title").inner_text().strip(), li.locator(".author").inner_text().strip(),
                        li.locator(".year").inner_text().strip()))
        return out

    def page_with(self, handler):
        page = self.open()
        page.route("**/books.json", handler)
        self.b.errors.clear()
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(100)
        return page

    def real_errors(self):
        return [e for e in self.b.errors if "Failed to load resource" not in e]

    def test_loads_sorted(self):
        page = self.open()
        page.wait_for_function("document.querySelectorAll('#book-list li.book').length > 0")
        self.assertEqual([b[0] for b in self.books(page)], ["Foundation", "Dune", "The Left Hand of Darkness", "Ubik",
                                                             "Children of Dune", "Neuromancer", "Hyperion"])
        self.assertEqual(self.books(page)[1], ("Dune", "Frank Herbert", "1965"))
        self.assertEqual(page.inner_text("#status").strip(), "Loaded 7 books")
        self.no_errors()

    def test_one_book_plain_text(self):
        body = json.dumps([{"title": "<i>Solaris</i>", "author": "Stanislaw Lem", "year": 1961}])
        page = self.page_with(lambda r: r.fulfill(status=200, content_type="application/json", body=body))
        self.assertEqual(self.books(page), [("<i>Solaris</i>", "Stanislaw Lem", "1961")])
        self.assertEqual(page.inner_text("#status").strip(), "Loaded 1 book")

    def test_http_error(self):
        page = self.page_with(lambda r: r.fulfill(status=500, body="oops"))
        self.assertEqual(page.inner_text("#status").strip(), "Could not load books")
        self.assertEqual(page.locator("#book-list li").count(), 0)
        self.assertEqual(self.real_errors(), [])

    def test_bad_json(self):
        page = self.page_with(lambda r: r.fulfill(status=200, content_type="application/json", body="{not json"))
        self.assertEqual(page.inner_text("#status").strip(), "Could not load books")
        self.assertEqual(self.real_errors(), [])
        page = self.page_with(lambda r: r.abort())
        self.assertEqual(page.inner_text("#status").strip(), "Could not load books")
        self.assertEqual(self.real_errors(), [])

    def test_loading_text(self):
        page = self.open()
        page.route("**/books.json", lambda r: None)  # never answered
        page.reload(wait_until="load")
        page.wait_for_timeout(200)
        self.assertEqual(page.inner_text("#status").strip(), "Loading...")
