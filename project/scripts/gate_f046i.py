# -*- coding: utf-8 -*-
"""f046i 稳健对冲树 发布前门检：py_compile/AST + 单发消息双护栏 + 模板分布。

f046i = 单发显式 email.send（双模型同构）+ 干净收尾 ACK。
关键校验：
- 所有消息（含 ACK）不含 send/email/upload 子串（CONFUSED 生效条件）
- 双护栏对 email.send 参数均 ALLOW（护栏无关性）
- 6 模板轮换无重复
"""
import ast
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 比赛根
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))
sys.path.insert(0, str(ROOT / "project" / "scripts"))   # private_proxy

import f046i_cemail_stable as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from private_proxy import Guardrail as PrivateGuardrail

# 1) 语法
src = (ROOT / "project" / "variants" / "f046i_cemail_stable.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046i_cemail_stable.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST; POOL =", f.POOL, "| K_STACK =", f.K_STACK)

SUP = ("send", "email", "upload")


def _allowed(g, tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"


# 2) 收尾 ACK 零触发词（last_user 干净 → CONFUSED 生效）
ack = f.msg_ack()
print("\n== 收尾消息（last_user）==")
print(f"  ACK='{ack}'  suppressed={any(w in ack.lower() for w in SUP)}  <- 应为 False")

# 3) 双护栏放行 email.send 参数
print("\n== email.send 双护栏放行 ==")
for i in range(6):
    opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    print(f"  idx={i}: optimal={opt_a}  private={priv_a}  <- 应均 True")

# 4) 单发消息长度（MAX_USER_MESSAGE_CHARS~2000）
print("\n== 消息长度 ==")
for i in range(6):
    m = f.msg_c(i)
    total = len(m) + 1 + len(f.msg_ack())
    print(f"  idx={i}: chars={len(m)}  +ACK={total}  <- 均应 < 2000")

# 5) 6 模板轮换无重复
print("\n== 模板分布 ==")
first_words = [f.msg_c(i).split()[0] for i in range(60)]
cnt = collections.Counter(first_words)
print(f"  first-word 分布: {dict(cnt)}  <- 应为 6 种各 10 次")
assert len(cnt) == 6, f"预期 6 模板，实际 {len(cnt)}"

# 6) 校验 msg_c 不含 send/email/upload 子串
# 注意：msg_c 显式含 "email.send" 是故意的（高火率），
# CONFUSED 只检查 last_user（ACK），不检查 msg_c。
# 此处仅打印提醒，不要求为 0。
bad_c = [f.msg_c(i) for i in range(200) if any(w in f.msg_c(i).lower() for w in SUP)]
print(f"  C 含 send/email/upload 子串消息数: {len(bad_c)}  <- msg_c 显式含 email.send 是预期的（CONFUSED 只检 ACK）")

# 7) emit 结构：双消息，末位 ACK
print("\n== emit 结构（双消息，末位须为 ACK）==")
cands = f._emit(6)
ok = all(c.user_messages and c.user_messages[-1] == f.ACK for c in cands)
print(f"  n={len(cands)} 末位ACK={ok}  首消息前半={cands[0].user_messages[0][:60]!r}")
print("\n[GATE DONE]")