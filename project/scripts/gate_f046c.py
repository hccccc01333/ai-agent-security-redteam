# -*- coding: utf-8 -*-
"""f046c 纯C池 发布前门检：py_compile/AST + C消息双护栏 + 池分布。"""
import ast
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 比赛根
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))
sys.path.insert(0, str(ROOT / "project" / "scripts"))   # private_proxy

import f046c_cc as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from private_proxy import Guardrail as PrivateGuardrail

# 1) 语法
src = (ROOT / "project" / "variants" / "f046c_cc.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046c_cc.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST")

SUP = ("send", "email", "upload")


def _allowed(g, tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"


# 2) C 单发（三种措辞 notify/alert/remind）：双护栏放行 + 不含 send/email/upload 子串
print("\n== C 单发（私榜 floor 主力）==")
for i in range(6):
    m = f.msg_c(i)
    last = m.lower()
    suppressed = any(w in last for w in SUP)
    opt_a = _allowed(OptimalGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    priv_a = _allowed(PrivateGuardrail(), "email.send", {"to": f"t{i}@x.co", "subject": "status", "body": "ok"})
    print(f"  C idx={i}: msg='{m}'  suppressed={suppressed}  optimal={opt_a}  private={priv_a}")

# 3) 池分布（纯 C：全槽 msg_c）与措辞轮换
print("\n== 池分布 ==")
cnt = collections.Counter(f._build(i)[0].split()[0] for i in range(200))
print("  pool by first-word:", dict(cnt))
c_tpls = collections.Counter(f.msg_c(i).split()[0] for i in range(12))
print("  C 措辞轮换:", dict(c_tpls))

# 4) 校验 C 消息无一含 send/email/upload 子串
bad = [f.msg_c(i) for i in range(200) if any(w in f.msg_c(i).lower() for w in SUP)]
print("  C 含 send/email/upload 子串的消息数:", len(bad), "<- 应为 0")

# 5) emit（HARD_N_CAP 内）分类解析
cands = f._emit(6)
print("  emit n=6 ok，首候选消息:", [c.messages[0][:40] if hasattr(c, 'messages') else c for c in cands])
print("\n[GATE DONE]")
