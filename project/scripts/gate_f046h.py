# -*- coding: utf-8 -*-
"""f046h 火率修复枪 发布前门检。

f046h = 显式 email.send 语法（f029 真实服务器验证 51.27/100% 火）+ k-stack forge + 干净收尾。
关键校验：LAST_USER 是收尾 ACK（零触发词）→ CONFUSED 每封 email +4；
msg1 显式含 send/email 是故意的（高火率），不计入 last_user。
"""
import ast
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 比赛根
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))
sys.path.insert(0, str(ROOT / "project" / "scripts"))   # private_proxy

import f046h_cemail_x as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from private_proxy import Guardrail as PrivateGuardrail

# 1) 语法
src = (ROOT / "project" / "variants" / "f046h_cemail_x.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046h_cemail_x.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST; K_STACK =", f.K_STACK, "| POOL =", f.POOL)

SUP = ("send", "email", "upload")


def _allowed(g, tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"


# 2) 收尾 ACK 零触发词（last_user 干净 → CONFUSED 生效）
ack = f.msg_ack()
print("\n== 收尾消息（last_user）==")
print(f"  ACK='{ack}'  suppressed={any(w in ack.lower() for w in SUP)}  <- 应为 False")

# 3) 双护栏放行 email.send 参数
print("\n== email.send 双护栏放行 ==")
opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": "t1@x.co", "subject": "status", "body": "ok"})
priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": "t1@x.co", "subject": "status", "body": "ok"})
print(f"  optimal={opt_a}  private={priv_a}  <- 应均 True")

# 4) 消息长度（MAX_USER_MESSAGE_CHARS~2000）
print("\n== 消息长度 ==")
m_c = f.msg_c(0)
m_k = f.msg_k(0)
print(f"  C 单发 chars={len(m_c)}  k-stack chars={len(m_k)}  +ACK={len(m_k + ' ' + f.msg_ack())}")

# 5) emit 结构：双消息，末位 ACK
print("\n== emit 结构（双消息，末位须为 ACK）==")
for stack in (False, True):
    cands = f._emit(3, stack=stack)
    ok = all(c.user_messages and c.user_messages[-1] == f.ACK for c in cands)
    print(f"  stack={stack}: n={len(cands)} 末位ACK={ok}  首消息前半={cands[0].user_messages[0][:60]!r}")
print("\n[GATE DONE]")