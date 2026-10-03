import unittest

from names.core import Registry


def registry(reserved=()):
    return Registry(min_len=2, max_len=12, cooldown_ms=5000, reserved=reserved)


class BasicTest(unittest.TestCase):
    def test_too_short_name(self):
        self.assertEqual(registry().check("a"), "error:length")

    def test_too_long_name(self):
        self.assertEqual(registry().check("a" * 20), "error:length")

    def test_reasonable_name_is_ok(self):
        self.assertEqual(registry().check("bob"), "ok")

    def test_unknown_owner_is_none(self):
        self.assertIsNone(registry().owner("ghost"))

    def test_scanned_starts_at_zero(self):
        self.assertEqual(registry().scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
