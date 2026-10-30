import random
import time
import unittest

from monitor.alerts import spread, windows_over
from monitor.rolling import rolling_max, rolling_min


def baseline():
    """CPU seconds this machine needs for a fixed piece of plain Python work (sorting 200k floats and 200k
    dict writes): the time limit below scales with the machine and its load instead of being a fixed number
    of seconds (process time, not wall time, so other programs running at the same time do not count)."""
    t0 = time.process_time()
    rnd = random.Random(0)
    xs = sorted(rnd.random() for _ in range(200_000))
    d = {}
    for i, x in enumerate(xs):
        d[i] = x
    return time.process_time() - t0


def slow(xs, k, f):
    return [f(xs[i:i + k]) for i in range(len(xs) - k + 1)]


class T(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(rolling_max([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])
        self.assertEqual(rolling_min([1, 3, -1, -3, 5, 3, 6, 7], 3), [-1, -3, -3, -3, 3, 3])
        self.assertEqual(rolling_max([4, 2], 1), [4, 2])
        self.assertEqual(rolling_max([4, 2], 3), [])
        self.assertEqual(rolling_min([], 2), [])
        self.assertEqual(rolling_max([2, 2, 2], 3), [2])
        for f in (rolling_max, rolling_min):
            with self.assertRaises(ValueError):
                f([1, 2], 0)
            with self.assertRaises(ValueError):
                f([1, 2], -1)

    def test_random(self):
        rnd = random.Random(5)
        for _ in range(300):
            xs = [rnd.randint(-5, 5) for _ in range(rnd.randint(0, 25))]
            k = rnd.randint(1, 27)
            copy = list(xs)
            self.assertEqual(rolling_max(xs, k), slow(xs, k, max))
            self.assertEqual(rolling_min(xs, k), slow(xs, k, min))
            self.assertEqual(xs, copy)

    def test_alerts(self):
        self.assertEqual(windows_over([1, 9, 1, 1, 1, 8], 2, 5), [0, 1, 4])
        self.assertEqual(spread([1, 4, 2, 8], 2), [3, 2, 6])

    def test_fast(self):
        rnd = random.Random(9)
        xs = [rnd.random() for _ in range(400_000)]
        budget = 25 * baseline()  # here (4-core Xeon 2.1 GHz): baseline 0.09 s, reference 0.21 s, starting code killed after 45 s
        t0 = time.process_time()
        hi = rolling_max(xs, 20_000)
        lo = rolling_min(xs, 20_000)
        took = time.process_time() - t0
        self.assertEqual(len(hi), 380_001)
        self.assertEqual(hi[0], max(xs[:20_000]))
        self.assertEqual(lo[-1], min(xs[-20_000:]))
        self.assertEqual(hi[123_456], max(xs[123_456:143_456]))
        self.assertLess(took, budget, f"took {took:.2f}s, budget {budget:.2f}s")
