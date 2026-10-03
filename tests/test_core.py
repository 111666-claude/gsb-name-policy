import time
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


class CharsetTest(unittest.TestCase):
    def test_space_and_bang_rejected(self):
        self.assertEqual(registry().check("bad name!"), "error:charset")

    def test_chinese_and_underscore_allowed(self):
        self.assertEqual(registry().check("英雄_1"), "ok")

    def test_all_digits_rejected(self):
        self.assertEqual(registry().check("12345"), "error:digits")

    def test_digits_with_letter_ok(self):
        self.assertEqual(registry().check("a123"), "ok")


class ReservedTest(unittest.TestCase):
    def test_reserved_name_rejected(self):
        self.assertEqual(registry(reserved=("admin",)).check("admin"),
                         "error:reserved")

    def test_cannot_claim_reserved(self):
        world = registry(reserved=("admin",))
        self.assertFalse(world.claim("admin", "p1", "r1", 0))
        self.assertIsNone(world.owner("admin"))


class ClaimTest(unittest.TestCase):
    def test_taken_name_not_overwritten(self):
        world = registry()
        self.assertTrue(world.claim("bob", "p1", "r1", 0))
        self.assertFalse(world.claim("bob", "p2", "r2", 0))
        self.assertEqual(world.owner("bob"), "p1")

    def test_same_owner_can_claim_again(self):
        world = registry()
        world.claim("bob", "p1", "r1", 0)
        self.assertTrue(world.claim("bob", "p1", "r2", 0))
        self.assertEqual(world.owner("bob"), "p1")

    def test_released_name_can_be_claimed(self):
        world = registry()
        world.claim("bob", "p1", "r1", 0)
        world.release("p1", 0)
        self.assertTrue(world.claim("bob", "p2", "r2", 0))
        self.assertEqual(world.owner("bob"), "p2")

    def test_invalid_name_cannot_be_claimed(self):
        world = registry()
        self.assertFalse(world.claim("123", "p1", "r1", 0))


class IdempotencyTest(unittest.TestCase):
    def test_claim_req_id_replays_result(self):
        world = registry()
        self.assertTrue(world.claim("bob", "p1", "r1", 0))
        self.assertTrue(world.claim("bob", "p2", "r1", 0))
        self.assertEqual(world.owner("bob"), "p1")

    def test_failed_claim_req_id_replays_false(self):
        world = registry()
        world.claim("bob", "p1", "r1", 0)
        self.assertFalse(world.claim("bob", "p2", "dup", 0))
        world.release("p1", 0)
        self.assertFalse(world.claim("bob", "p2", "dup", 10))
        self.assertIsNone(world.owner("bob"))


class CooldownTest(unittest.TestCase):
    def test_rename_within_cooldown_fails(self):
        world = registry()
        self.assertTrue(world.rename("p1", "alice", "r1", 0))
        self.assertFalse(world.rename("p1", "alice2", "r2", 1))
        self.assertEqual(world.owner("alice"), "p1")
        self.assertIsNone(world.owner("alice2"))

    def test_rename_after_cooldown_succeeds(self):
        world = registry()
        world.rename("p1", "alice", "r1", 0)
        self.assertTrue(world.rename("p1", "alice2", "r2", 5000))
        self.assertIsNone(world.owner("alice"))
        self.assertEqual(world.owner("alice2"), "p1")

    def test_rename_cannot_take_occupied_name(self):
        world = registry()
        world.rename("p1", "alice", "r1", 0)
        self.assertFalse(world.rename("p2", "alice", "r2", 100000))
        self.assertEqual(world.owner("alice"), "p1")

    def test_rename_req_id_is_idempotent(self):
        world = registry()
        world.rename("p1", "alice", "r1", 0)
        self.assertFalse(world.rename("p1", "alice2", "r2", 1))
        self.assertFalse(world.rename("p1", "alice2", "r2", 100000))
        self.assertIsNone(world.owner("alice2"))


class ScanCostTest(unittest.TestCase):
    def test_check_does_not_scan_all_names(self):
        world = registry()
        for index in range(10000):
            world.claim("n%d" % index, "p%d" % index, "r%d" % index, 0)
        start = world.scanned_count()
        for _ in range(3000):
            world.check("n9999")
        self.assertEqual(world.scanned_count(), start)

    def test_100k_names_throughput(self):
        world = registry()
        for index in range(100000):
            world.claim("n%d" % index, "p%d" % index, "r%d" % index, 0)
        begin = time.perf_counter()
        for _ in range(100000):
            world.check("n99999")
        elapsed = time.perf_counter() - begin
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
