# name-policy

角色名策略：字符集与长度规则、保留名、占用台账与改名冷却，只用 Python 标准库。

```
python3 -m names.cli --sample charset
python3 -m names.cli --sample reserved
python3 -m names.cli --sample taken
python3 -m names.cli --sample cooldown
python3 -m names.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **长度**：名字长度必须落在 `[min_len, max_len]`，否则 `error:length`。
- **字符集**：只允许字母、数字、下划线、汉字，否则 `error:charset`。
- **纯数字**：全是数字的名字返回 `error:digits`。
- **保留名**：命中 `reserved` 的名字返回 `error:reserved`。
- **占用**：一个名字只能被一个玩家占用；已被别人占用的名字 `claim` 返回 False
  且不改动原占用者。
- **幂等**：同一个 `req_id` 只生效一次，重复调用返回上次结果。
- **改名冷却**：同一个玩家距上次改名不足 `cooldown_ms` 时改名返回 False。
- **释放**：`release` 之后名字可以被别人占用。
- **查询代价**：`check` 与 `claim` 不许扫描全部已占用名字，`scanned_count`
  不随名字数线性增长。
- **规模**：10 万个名字、每秒 10 万次校验，单次摊还 O(1)。

## 输出契约（不改格式）

```
result=..
second=..
scanned=..
```

## 目录

```
names/core.py   规则、占用、幂等与冷却
names/cli.py    命令行入口
tests/          unittest 用例
```
