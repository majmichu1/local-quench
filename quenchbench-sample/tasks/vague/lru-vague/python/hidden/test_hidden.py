import unittest
from lru import LRUCache


class T(unittest.TestCase):
    def test_get_refreshes(self):
        c = LRUCache(2)
        c.put('a', 1); c.put('b', 2); c.get('a'); c.put('c', 3)
        self.assertIsNone(c.get('b'))
        self.assertEqual(c.get('a'), 1)

    def test_put_refreshes(self):
        c = LRUCache(2)
        c.put('a', 1); c.put('b', 2); c.put('a', 10); c.put('c', 3)
        self.assertEqual(c.get('a'), 10)
        self.assertIsNone(c.get('b'))
