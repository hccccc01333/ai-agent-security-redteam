# -*- coding: utf-8 -*-
"""f046e2 forge k-email 双池轮换 发布前门检：py_compile/AST + 双池消息双护栏 + 池分布。"""
import ast
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 比赛根
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))
sys.path.insert(0, str(ROOT / "project" / "scripts"))   # private_proxy

import f046e2_cemail_k as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from private_proxy import Guardrail as PrivateGuardrail

src = (ROOT / "project" / "variants" / "f046e2_cemail_k.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046e2_cemail_k.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST; K_STACK =", f.K_STACK)

SUP = ("send", "email", "upload")


def _allowed(g, tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"


print("\n== k-email 双池消息（gpt_oss forge）==")
for i in range(6):
    m = f.msg_k(i)
    pool = "A" if i % 2 == 0 else "B"
    last = m.lower()
    suppressed = any(w in last for w in SUP)
    opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": f"x{i}@x.co", "subject": "status", "body": "ok"})
    priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": f"x{i}@x.co", "subject": "status", "body": "ok"})
    print(f"  idx={i} pool={pool}: chars={len(m)}  suppressed={suppressed}  optimal={opt_a}  private={priv_a}")

print("\n== C 单发（gemma 快行 / 退化兜底）==")
for i in range(3):
    m = f.msg_c(i)
    suppressed = any(w in m.lower() for w in SUP)
    print(f"  C idx={i}: suppressed={suppressed}")

print("\n== 池分布（A 偶数 / B 奇数）==")
k_first = collections.Counter("A" if i % 2 == 0 else "B" for i in range(60))
print("  k pool by parity:", dict(k_first))
bad = [f.msg_k(i) for i in range(60) if any(w in f.msg_k(i).lower() for w in SUP)]
print("  k 含 send/email/upload 子串消息数:", len(bad), "<- 应为 0")
bad_c = [f.msg_c(i) for i in range(200) if any(w in f.msg_c(i).lower() for w in SUP)]
print("  C 含 send/email/upload 子串消息数:", len(bad_c), "<- 应为 0")

cands_k = f._emit(6, stack=True)
print("  emit k n=6 ok，首候选:", [c.messages[0][:40] if hasattr(c, 'messages') else str(c)[:40] for c in cands_k])
print("\n[GATE DONE]")
