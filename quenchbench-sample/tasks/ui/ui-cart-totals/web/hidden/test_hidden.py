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


class T(UITest):
    def summary(self, page):
        return tuple(page.inner_text("#" + k).strip() for k in ("subtotal", "discount", "shipping", "total", "cart-count"))

    def row(self, sku):
        return f'#cart tr[data-sku="{sku}"]'

    def promo(self, page, code):
        page.fill("#promo", code)
        page.click("#apply-promo")

    def test_initial(self):
        page = self.open()
        self.assertEqual(self.summary(page), ("$192.94", "$0.00", "$0.00", "$192.94", "4"))
        self.assertEqual(page.inner_text(self.row("mouse") + " .line-total").strip(), "$50.00")
        self.assertEqual(page.inner_text(self.row("kb") + " .price").strip(), "$129.99")
        self.no_errors()

    def test_max_and_thousands(self):
        page = self.open()
        for _ in range(9):
            page.click(self.row("kb") + " .qty-inc")
        self.assertEqual(page.inner_text(self.row("kb") + " .qty").strip(), "10")
        self.assertTrue(page.locator(self.row("kb") + " .qty-inc").is_disabled())
        self.assertFalse(page.locator(self.row("mouse") + " .qty-inc").is_disabled())
        self.assertEqual(page.inner_text(self.row("kb") + " .line-total").strip(), "$1,299.90")
        self.assertEqual(self.summary(page), ("$1,362.85", "$0.00", "$0.00", "$1,362.85", "13"))
        self.promo(page, "  save10 ")
        self.assertEqual(page.inner_text("#promo-msg").strip(), "SAVE10 applied")
        self.assertEqual(self.summary(page), ("$1,362.85", "-$136.29", "$0.00", "$1,226.56", "13"))
        self.no_errors()

    def test_promo_and_shipping(self):
        page = self.open()
        self.promo(page, "SAVE10")
        self.assertEqual(self.summary(page), ("$192.94", "-$19.29", "$0.00", "$173.65", "4"))
        page.click(self.row("kb") + " .qty-dec")
        self.assertEqual(page.locator(self.row("kb")).count(), 0)
        self.assertEqual(self.summary(page), ("$62.95", "-$6.30", "$0.00", "$56.65", "3"))
        page.click(self.row("cable") + " .qty-dec")
        self.assertEqual(self.summary(page), ("$50.00", "-$5.00", "$5.99", "$50.99", "2"))
        self.promo(page, "SAVE20")
        self.assertEqual(page.inner_text("#promo-msg").strip(), "Invalid code")
        self.assertEqual(self.summary(page), ("$50.00", "$0.00", "$0.00", "$50.00", "2"))
        page.click(self.row("mouse") + " .qty-dec")
        self.assertEqual(self.summary(page), ("$25.00", "$0.00", "$5.99", "$30.99", "1"))
        page.click(self.row("mouse") + " .qty-dec")
        self.assertEqual(page.locator("#cart tbody tr").count(), 0)
        self.assertEqual(self.summary(page), ("$0.00", "$0.00", "$0.00", "$0.00", "0"))
        self.no_errors()
