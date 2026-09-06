# -*- coding: utf-8 -*-
"""校验 notebook 所有 code cell 语法。用法: python _validate_nb.py <path.ipynb>"""
import ast
import json
import sys

nb = json.load(open(sys.argv[1], encoding="utf-8"))
ok = True
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"])
    try:
        ast.parse(src)
        print(f"cell {i}: SYNTAX_OK ({len(src)} chars)")
    except SyntaxError as e:
        ok = False
        print(f"cell {i}: SYNTAX_FAIL line {e.lineno}: {e.msg}")
print("ALL_OK" if ok else "HAS_FAIL")
