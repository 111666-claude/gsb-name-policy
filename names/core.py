"""角色名策略：字符集与长度规则、保留名、占用台账与改名冷却。

缺陷：不校验字符集、不拦保留名、不拦纯数字、占用不检查（同名可被覆盖）、
改名冷却不生效、每次校验扫描全部已占用名字。
"""

import re

ALLOWED = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]+$")


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
        self.scanned += len(self.names)
        if len(name) < self.min_len or len(name) > self.max_len:
            return "error:length"
        return "ok"

    def claim(self, name, player, req_id, now_ms):
        """占用一个名字。"""
        if req_id in self.reqs:
            return self.reqs[req_id]
        self.names[name] = player
        self.reqs[req_id] = True
        return True

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
        self.names[name] = player
        self.reqs[req_id] = True
        return True

    def owner(self, name):
        return self.names.get(name)

    def scanned_count(self):
        return self.scanned
