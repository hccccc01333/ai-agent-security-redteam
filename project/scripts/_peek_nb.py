# -*- coding: utf-8 -*-
"""临时工具：查看 notebook cell 结构"""
import json
import sys

p = sys.argv[1]
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9

full = "--full" in sys.argv
nb = json.load(open(p, encoding="utf-8"))
print("cells:", len(nb["cells"]))
for i, c in enumerate(nb["cells"]):
    if not (start <= i < end):
        continue
    src = "".join(c["source"])
    print(f"--- cell {i} [{c['cell_type']}] {len(src)} chars ---")
    print(src if full else src[:400])
    print()
