"""角色名策略：字符集与长度规则、保留名、占用台账与改名冷却。"""

import re

ALLOWED = re.compile(r"^[A-Za-z0-9_一-鿿]+$")
DIGITS = re.compile(r"^[0-9]+$")


class Registry:
    """名字占用台账。"""

    def __init__(self, min_len, max_len, cooldown_ms, reserved=()):
        self.min_len = min_len
        self.max_len = max_len
        self.cooldown_ms = cooldown_ms
        self.reserved = set(reserved)
        self.names = {}
        self.reqs = {}
        self.last_rename = {}
        self.scanned = 0

    def check(self, name):
        """校验名字格式，返回 ok 或 error:xxx。"""
        if len(name) < self.min_len or len(name) > self.max_len:
            return "error:length"
        if not ALLOWED.match(name):
            return "error:charset"
        if DIGITS.match(name):
            return "error:digits"
        if name in self.reserved:
            return "error:reserved"
        return "ok"

    def claim(self, name, player, req_id, now_ms):
        """占用一个名字。"""
        if req_id in self.reqs:
            return self.reqs[req_id]
        result = self.check(name) == "ok" and (
            self.names.get(name) in (None, player)
        )
        if result:
            self.names[name] = player
        self.reqs[req_id] = result
        return result

    def release(self, player, now_ms):
        """释放该玩家占用的名字。"""
        for name in list(self.names):
            if self.names[name] == player:
                del self.names[name]
        return True

    def rename(self, player, name, req_id, now_ms):
        """改名。"""
        if req_id in self.reqs:
            return self.reqs[req_id]
        last = self.last_rename.get(player)
        result = (
            self.check(name) == "ok"
            and (last is None or now_ms - last >= self.cooldown_ms)
            and self.names.get(name) in (None, player)
        )
        if result:
            self.release(player, now_ms)
            self.names[name] = player
            self.last_rename[player] = now_ms
        self.reqs[req_id] = result
        return result

    def owner(self, name):
        return self.names.get(name)

    def scanned_count(self):
        return self.scanned
