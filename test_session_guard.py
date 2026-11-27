"""Regression tests for the bounded local session store."""
import unittest
from session_guard import SessionStore


class SessionStoreTests(unittest.TestCase):
    def test_reuse_and_capacity(self):
        store = SessionStore(lambda: object(), max_sessions=2)
        a = store.get_or_create("a")
        self.assertIs(a, store.get_or_create("a"))
        store.get_or_create("b")
        store.get_or_create("c")
        self.assertEqual(len(store), 2)
        self.assertIsNot(a, store.get_or_create("a"))

    def test_clear(self):
        store = SessionStore(lambda: object())
        store.get_or_create("a")
        self.assertTrue(store.clear("a"))
        self.assertFalse(store.clear("a"))
        self.assertEqual(len(store), 0)

    def test_reject_bad_ids(self):
        store = SessionStore(lambda: object())
        for value in ("", "x" * 129):
            with self.assertRaises(ValueError):
                store.get_or_create(value)

    def test_idle_expiry(self):
        store = SessionStore(lambda: object(), idle_seconds=0.001)
        first = store.get_or_create("a")
        import time
        time.sleep(0.01)
        self.assertIsNot(first, store.get_or_create("a"))


if __name__ == "__main__":
    unittest.main()
