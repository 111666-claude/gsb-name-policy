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

    def test_chinese_and_underscore_ok(self):
        self.assertEqual(registry().check("小明_1"), "ok")

    def test_all_digits_rejected(self):
        self.assertEqual(registry().check("12345"), "error:digits")


class ReservedTest(unittest.TestCase):
    def test_reserved_name_rejected(self):
        self.assertEqual(registry(reserved=("admin",)).check("admin"),
                         "error:reserved")

    def test_non_reserved_name_ok(self):
        self.assertEqual(registry(reserved=("admin",)).check("admin2"), "ok")


class ClaimTest(unittest.TestCase):
    def test_taken_name_rejected_and_owner_kept(self):
        world = registry()
        self.assertTrue(world.claim("bob", "p1", "r1", 0))
        self.assertFalse(world.claim("bob", "p2", "r2", 0))
        self.assertEqual(world.owner("bob"), "p1")

    def test_same_player_reclaim_ok(self):
        world = registry()
        self.assertTrue(world.claim("bob", "p1", "r1", 0))
        self.assertTrue(world.claim("bob", "p1", "r2", 0))
        self.assertEqual(world.owner("bob"), "p1")


class IdempotencyTest(unittest.TestCase):
    def test_same_req_id_returns_cached_result(self):
        world = registry()
        self.assertTrue(world.claim("bob", "p1", "r1", 0))
        self.assertTrue(world.claim("alice", "p2", "r1", 0))
        self.assertIsNone(world.owner("alice"))

    def test_failed_result_memoized(self):
        world = registry()
        world.claim("bob", "p1", "r1", 0)
        self.assertFalse(world.claim("bob", "p2", "r2", 0))
        world.release("p1", 0)
        self.assertFalse(world.claim("bob", "p2", "r2", 0))
        self.assertIsNone(world.owner("bob"))


class CooldownTest(unittest.TestCase):
    def test_rename_within_cooldown_rejected(self):
        world = registry()
        self.assertTrue(world.rename("p1", "alice", "r1", 0))
        self.assertFalse(world.rename("p1", "alice2", "r2", 1))
        self.assertIsNone(world.owner("alice2"))

    def test_rename_after_cooldown_ok(self):
        world = registry()
        self.assertTrue(world.rename("p1", "alice", "r1", 0))
        self.assertTrue(world.rename("p1", "alice2", "r2", 5000))
        self.assertEqual(world.owner("alice2"), "p1")

    def test_rename_frees_old_name(self):
        world = registry()
        world.rename("p1", "alice", "r1", 0)
        world.rename("p1", "alice2", "r2", 5000)
        self.assertIsNone(world.owner("alice"))
        self.assertTrue(world.claim("alice", "p2", "r3", 5000))

    def test_rename_to_taken_name_rejected(self):
        world = registry()
        world.claim("bob", "p2", "r0", 0)
        self.assertFalse(world.rename("p1", "bob", "r1", 10000))
        self.assertEqual(world.owner("bob"), "p2")


class ReleaseTest(unittest.TestCase):
    def test_release_frees_name_for_others(self):
        world = registry()
        world.claim("bob", "p1", "r1", 0)
        world.release("p1", 0)
        self.assertIsNone(world.owner("bob"))
        self.assertTrue(world.claim("bob", "p2", "r2", 0))
        self.assertEqual(world.owner("bob"), "p2")


class ScanCostTest(unittest.TestCase):
    def test_check_and_claim_do_not_scan_names(self):
        world = registry()
        for index in range(5000):
            world.claim("name-%d" % index, "p-%d" % index, "r-%d" % index, 0)
        for _ in range(5000):
            world.check("name-0")
        self.assertEqual(world.scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
