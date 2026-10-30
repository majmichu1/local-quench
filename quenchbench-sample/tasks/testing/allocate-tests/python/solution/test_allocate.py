import unittest

from billing.allocate import allocate


class AllocateTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(allocate(100, [1, 1]), [50, 50])
        self.assertEqual(allocate(10, [6, 3, 1]), [6, 3, 1])

    def test_sum_and_ties(self):
        self.assertEqual(allocate(100, [1, 1, 1]), [34, 33, 33])
        self.assertEqual(allocate(2, [1, 1, 1]), [1, 1, 0])

    def test_largest_remainder(self):
        self.assertEqual(allocate(5, [6, 3, 1]), [3, 2, 0])
        self.assertEqual(allocate(7, [5, 3, 2]), [4, 2, 1])
        for total in range(0, 40):
            self.assertEqual(sum(allocate(total, [3, 5, 7, 0])), total)

    def test_zero_weight(self):
        self.assertEqual(allocate(5, [1, 0, 1]), [3, 0, 2])

    def test_errors(self):
        for total, weights in ((-1, [1]), (10, []), (10, [0, 0]), (10, [2, -1])):
            with self.assertRaises(ValueError):
                allocate(total, weights)
