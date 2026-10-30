import ast
import subprocess
import sys
import unittest

import app
import metrics
import ratelimit
import ratelimit.bucket
import ratelimit.limiter


class T(unittest.TestCase):
    def test_structure(self):
        self.assertIs(ratelimit.TokenBucket, ratelimit.bucket.TokenBucket)
        self.assertIs(ratelimit.RateLimiter, ratelimit.limiter.RateLimiter)
        self.assertEqual(ratelimit.bucket.TokenBucket.__module__, 'ratelimit.bucket')
        self.assertEqual(ratelimit.limiter.RateLimiter.__module__, 'ratelimit.limiter')
        self.assertIs(app.TokenBucket, ratelimit.bucket.TokenBucket)
        self.assertIs(app.RateLimiter, ratelimit.limiter.RateLimiter)
        tree = ast.parse(open('app.py').read())
        self.assertFalse([n.name for n in tree.body if isinstance(n, ast.ClassDef)], 'app.py defines classes')
        code = 'import sys, ratelimit; sys.exit(1 if "app" in sys.modules else 0)'
        r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, 'ratelimit must not import app ' + r.stderr)

    def test_bucket(self):
        b = ratelimit.TokenBucket(2, 1.0, now=0.0)
        self.assertEqual([b.allow(0), b.allow(0), b.allow(0)], [True, True, False])
        self.assertFalse(b.allow(0.5))
        self.assertTrue(b.allow(1.6))
        self.assertFalse(b.allow(1.0))
        with self.assertRaises(ValueError):
            ratelimit.TokenBucket(0, 1)
        with self.assertRaises(ValueError):
            ratelimit.TokenBucket(1, 0)

    def test_limiter_and_app(self):
        lim = app.RateLimiter(1, 0.5)
        self.assertEqual(app.handle_request(lim, 'a', '/health', 0), (200, 'ok'))
        self.assertEqual(app.handle_request(lim, 'a', '/health', 1), (429, 'slow down'))
        self.assertEqual(app.handle_request(lim, 'b', '/x', 1), (404, 'not found'))
        self.assertEqual(app.handle_request(lim, 'a', '/health', 3), (200, 'ok'))
        self.assertEqual(lim.stats(), {'allowed': 3, 'denied': 1, 'clients': 2})
        self.assertEqual(metrics.deny_ratio(lim), 0.25)
        self.assertEqual(metrics.deny_ratio(ratelimit.RateLimiter(1, 1)), 0.0)
