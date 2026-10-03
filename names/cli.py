"""命令行入口：跑角色名样例。"""

import argparse

from .core import Registry


def build_parser():
    parser = argparse.ArgumentParser(prog="name-policy", description="角色名策略")
    parser.add_argument("--sample", default="charset",
                        help="charset / reserved / taken / cooldown / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "charset":
        world = Registry(min_len=2, max_len=12, cooldown_ms=0)
        print("result=%s" % world.check("bad name!"))
    elif args.sample == "reserved":
        world = Registry(min_len=2, max_len=12, cooldown_ms=0, reserved=("admin",))
        print("result=%s" % world.check("admin"))
    elif args.sample == "taken":
        world = Registry(min_len=2, max_len=12, cooldown_ms=0)
        world.claim("bob", "p1", "r1", 0)
        ok = world.claim("bob", "p2", "r2", 0)
        print("second=%s owner=%s" % (str(ok).lower(), world.owner("bob")))
    elif args.sample == "cooldown":
        world = Registry(min_len=2, max_len=12, cooldown_ms=5000)
        world.rename("p1", "alice", "r1", 0)
        ok = world.rename("p1", "alice2", "r2", 1)
        print("second=%s" % str(ok).lower())
    elif args.sample == "scan":
        world = Registry(min_len=2, max_len=12, cooldown_ms=0)
        for index in range(3000):
            world.claim("name-%d" % index, "p-%d" % index, "r-%d" % index, 0)
        for index in range(3000):
            world.check("name-2999")
        print("scanned=%d" % world.scanned_count())
    else:
        raise SystemExit("需要 --sample charset|reserved|taken|cooldown|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
