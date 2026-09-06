# -*- coding: utf-8 -*-
"""f046b2 发布前静态门检：语法 + C/R 池分布 + C 无触发词 + emit 解析。"""
import ast
import collections
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT / "project" / "variants"))

import f046b2_rb64 as f
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail

# 1) 语法
src = (ROOT / "project" / "variants" / "f046b2_rb64.py").read_text(encoding="utf-8")
py_compile.compile(str(ROOT / "project" / "variants" / "f046b2_rb64.py"), doraise=True)
ast.parse(src)
print("[PASS] py_compile + AST")

# 2) C 消息不含 send/email/upload 子串（guardrail deny 触发词）
SUP = ("send", "email", "upload")
bad_c = [f.msg_c(i) for i in range(60) if any(w in f.msg_c(i).lower() for w in SUP)]
print("C 含 send/email/upload 子串数:", len(bad_c), "<- 应 0")

# 3) 池分布（C_SPLIT 前后 C vs R）
cnt = collections.Counter("C" if s < f.C_SPLIT else "R" for s in [(i % 1000) / 1000.0 for i in range(200)])
print("池分布 C/R:", dict(cnt))

# 4) R 消息含 fs.read + http.post + base64 指令（确保重放读 secret 通道存在）
for i in [200, 701, 999]:
    m = f.msg_r(i)
    low = m.lower()
    print(f"R idx={i}: read={('fs.read' in low)} post={('http.post' in low)} b64={('base64' in low)} url_ok={('http://' in low)}")

# 5) emit 解析（HARD_N_CAP 内）
cands = f._emit(8)
print("emit n=8 ok; 首候选:", [c.messages[0][:45] if hasattr(c, 'messages') else c for c in cands[:3]])

# 6) C 候选在公榜 email.send 放行
g = OptimalGuardrail()
def _allow(tn, args):
    return g.decide(tn, args, {"recent_sources": []}).action == "ALLOW"
c_allow = _allow("email.send", {"to": "t1@x.co", "subject": "status", "body": "ok"})
print("公榜 email.send(to/status/body=ok) allow:", c_allow)

print("\n[GATE DONE]")