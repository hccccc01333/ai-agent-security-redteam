"""Submission validator (Frontis-MA1 'submission_validator' adaptation).

Checks that a variant satisfies the competition submission contract before it
is pushed: valid AST, AttackAlgorithm(AttackAlgorithmBase) class with run(),
and no forbidden runtime features (network libs, subprocess, stdin).

Usage (from project/):
  python scripts/validate_submission.py variants/x4_https.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

FORBIDDEN = [
    "import requests",
    "from requests",
    "import socket",
    "import http.client",
    "import subprocess",
    "os.system",
    "os.popen",
    "input(",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate attack submission contract")
    ap.add_argument("--variant", required=True)
    args = ap.parse_args()

    path = Path(args.variant)
    if not path.exists():
        print(f"FAIL variant not found: {path}", file=sys.stderr)
        return 1
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as err:
        print(f"FAIL ast: {err}", file=sys.stderr)
        return 1

    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "AttackAlgorithm"), None)
    if cls is None:
        print("FAIL class AttackAlgorithm not found", file=sys.stderr)
        return 1
    bases = [ast.unparse(b) for b in cls.bases]
    if not any("AttackAlgorithmBase" in b for b in bases):
        print(f"FAIL AttackAlgorithm must inherit AttackAlgorithmBase, got {bases}", file=sys.stderr)
        return 1
    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    if "run" not in methods:
        print("FAIL method run() not found", file=sys.stderr)
        return 1

    bad = [f for f in FORBIDDEN if f in src]
    if bad:
        print(f"FAIL forbidden features: {bad}", file=sys.stderr)
        return 1

    print(f"PASS {path.name}: AttackAlgorithm(run) OK, no forbidden features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
