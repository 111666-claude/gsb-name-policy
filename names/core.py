"""角色名策略：字符集与长度规则、保留名、占用台账与改名冷却。"""

import re

ALLOWED = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]+$")


class Registry:
    """名字占用台账。check 与 claim 均为摊还 O(1)，不扫描已占用名字。"""

    def __init__(self, min_len, max_len, cooldown_ms, reserved=()):
        self.min_len = min_len
        self.max_len = max_len
        self.cooldown_ms = cooldown_ms
        self.reserved = set(reserved)
        self.names = {}
        self.player_names = {}
        self.reqs = {}
        self.last_rename = {}
        self.scanned = 0

    def check(self, name):
        """校验名字格式，返回 ok 或 error:xxx。"""
        if len(name) < self.min_len or len(name) > self.max_len:
            return "error:length"
        if not ALLOWED.match(name):
            return "error:charset"
        if name.isdigit():
            return "error:digits"
        if name in self.reserved:
            return "error:reserved"
        return "ok"

    def claim(self, name, player, req_id, now_ms):
        """占用一个名字；已被别人占用返回 False 且不改动原占用者。"""
        if req_id in self.reqs:
            return self.reqs[req_id]
        owner = self.names.get(name)
        if owner is not None and owner != player:
            self.reqs[req_id] = False
            return False
        if owner is None:
            self.names[name] = player
            self.player_names.setdefault(player, set()).add(name)
        self.reqs[req_id] = True
        return True

    def release(self, player, now_ms):
        """释放该玩家占用的全部名字。"""
        for name in self.player_names.pop(player, ()):
            if self.names.get(name) == player:
                del self.names[name]
        return True

    def rename(self, player, name, req_id, now_ms):
        """改名：冷却期内或目标名字被别人占用时返回 False。"""
        if req_id in self.reqs:
            return self.reqs[req_id]
        last = self.last_rename.get(player)
        if last is not None and now_ms - last < self.cooldown_ms:
            self.reqs[req_id] = False
            return False
        owner = self.names.get(name)
        if owner is not None and owner != player:
            self.reqs[req_id] = False
            return False
        for old in self.player_names.get(player, ()):
            if old != name and self.names.get(old) == player:
                del self.names[old]
        self.names[name] = player
        self.player_names[player] = {name}
        self.last_rename[player] = now_ms
        self.reqs[req_id] = True
        return True

    def owner(self, name):
        return self.names.get(name)

    def scanned_count(self):
        return self.scanned
