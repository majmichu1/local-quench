"""Helper for UI checks: serve the task folder over HTTP and open it in headless Chromium.

Copied next to the hidden tests when a UI task is graded. Usage in a test:

    from forge_ui import Browser

    class T(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.b = Browser()

        @classmethod
        def tearDownClass(cls):
            cls.b.close()

        def test_x(self):
            page = self.b.open("index.html")
            ...
            self.assertEqual(self.b.errors, [])
"""

import functools
import http.server
import os
import threading

from playwright.sync_api import sync_playwright


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Browser:
    def __init__(self, root=".", width=1280, height=800):
        handler = functools.partial(_Quiet, directory=os.path.abspath(root))
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}/"
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch()
        self.width, self.height = width, height
        self.errors = []

    def open(self, path="index.html", width=None, height=None):
        """A fresh page at the given size; console errors and uncaught exceptions go to self.errors."""
        self.errors = []
        page = self.browser.new_page(viewport={"width": width or self.width, "height": height or self.height})
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and self.errors.append(m.text))
        page.goto(self.base + path)
        page.wait_for_load_state("networkidle")
        return page

    def close(self):
        self.browser.close()
        self.pw.stop()
        self.server.shutdown()
