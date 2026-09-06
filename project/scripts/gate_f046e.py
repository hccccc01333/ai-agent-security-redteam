# -*- coding: utf-8 -*-
"""f046e forge k-email 叠加池 发布前门检：py_compile/AST + C/k-email 消息双护栏 + 池分布。"""
import ast
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 比赛根
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))
sys.path.insert(0, str(ROOT / "project" / "scripts"))   # private_proxy

import f046e_cemail_k as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from private_proxy import Guardrail as PrivateGuardrail

# 1) 语法
src = (ROOT / "project" / "variants" / "f046e_cemail_k.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046e_cemail_k.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST; K_STACK =", f.K_STACK)

SUP = ("send", "email", "upload")


def _allowed(g, tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"


# 2) C 单发 + k-email 消息：双护栏放行 + 不含 send/email/upload 子串
print("\n== C 单发（gemma 快行 / 退化兜底）==")
for i in range(3):
    m = f.msg_c(i)
    last = m.lower()
    suppressed = any(w in last for w in SUP)
    opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    print(f"  C idx={i}: msg='{m}'  suppressed={suppressed}  optimal={opt_a}  private={priv_a}")

print(f"\n== k-email 消息（gpt_oss forge, K_STACK={f.K_STACK}）==")
for i in range(3):
    m = f.msg_k(i)
    last = m.lower()
    suppressed = any(w in last for w in SUP)
    opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": f"t{i*f.K_STACK}@x.co", "subject": "status", "body": "ok"})
    priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": f"t{i*f.K_STACK}@x.co", "subject": "status", "body": "ok"})
    print(f"  k idx={i}: chars={len(m)}  suppressed={suppressed}  optimal={opt_a}  private={priv_a}")
    print(f"    msg={m[:140]}...")

# 3) 池分布
print("\n== 池分布 ==")
cnt = collections.Counter(f.msg_c(i).split()[0] for i in range(200))
print("  C pool by first-word:", dict(cnt))
k_first = collections.Counter(f.msg_k(i).split()[0] for i in range(50))
print("  k pool by first-word:", dict(k_first))

# 4) 校验 C/k 消息无一含 send/email/upload 子串
bad_c = [f.msg_c(i) for i in range(200) if any(w in f.msg_c(i).lower() for w in SUP)]
bad_k = [f.msg_k(i) for i in range(50) if any(w in f.msg_k(i).lower() for w in SUP)]
print("  C 含 send/email/upload 子串消息数:", len(bad_c), "<- 应为 0")
print("  k 含 send/email/upload 子串消息数:", len(bad_k), "<- 应为 0")

# 5) emit 分类解析：C 与 k
cands_c = f._emit(6, stack=False)
cands_k = f._emit(6, stack=True)
print("  emit C n=6 ok，首候选:", [c.messages[0][:40] if hasattr(c, 'messages') else str(c)[:40] for c in cands_c])
print("  emit k n=6 ok，首候选:", [c.messages[0][:40] if hasattr(c, 'messages') else str(c)[:40] for c in cands_k])
print("\n[GATE DONE]")
