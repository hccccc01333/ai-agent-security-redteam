#!/usr/bin/env python3
"""Kaggle competition discipline gates.

Usage:
  python check_discipline.py [--gate G0|G1|G2|G3]

Project root comes from KAGGLE_PROJECT_DIR env var, else current directory.
Exit code 0 means all selected gates PASS.
"""

import argparse
import os
import re
import sys
from pathlib import Path


def project_dir() -> Path:
    env = os.environ.get("KAGGLE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path.cwd()


def gate0(p: Path):
    """立项门：至少 2 个不同构思路 + 立项检查单存在。"""
    issues = []
    idx = p / "01_frameworks" / "_index.md"
    if not idx.exists():
        issues.append("缺少 01_frameworks/_index.md")
    else:
        n = len(re.findall(r"^\|\s*F\d+", idx.read_text(encoding="utf-8"), re.M))
        if n < 2:
            issues.append(f"思路数 {n} < 2")
    if not (p / "00_playbook" / "01_project_design.md").exists() and not (
        p / "project_design.md"
    ).exists():
        issues.append("缺少立项检查单 (00_playbook/01_project_design.md)")
    return issues


def gate1(p: Path):
    """实验门：每个方案子库必须有 PLAN.md 和非空 component_log.csv。"""
    issues = []
    exp_root = p / "03_experiments"
    logs = sorted(exp_root.glob("*/*/component_log.csv")) if exp_root.exists() else []
    for log in logs:
        lines = log.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) < 2:
            issues.append(f"{log.relative_to(p)} 没有实验记录")
        if not log.with_name("PLAN.md").exists():
            issues.append(f"{log.parent.relative_to(p)} 缺少 PLAN.md")
    return issues


def gate2(p: Path):
    """结论门：每条结论必须有重开条件与失败分类。"""
    issues = []
    concl_root = p / "04_conclusions"
    concls = (
        sorted(c for c in concl_root.glob("*.md") if not c.name.startswith("_"))
        if concl_root.exists()
        else []
    )
    for c in concls:
        text = c.read_text(encoding="utf-8")
        if "重开条件" not in text:
            issues.append(f"{c.name} 缺少重开条件")
        if "失败分类" not in text:
            issues.append(f"{c.name} 缺少失败分类")
    return issues


def gate3(p: Path):
    """提交门：批准提交前必须存在墙生存报告。"""
    issues = []
    if (p / "submission_approved.txt").exists() and not (
        p / "reports" / "wall_survival.md"
    ).exists():
        issues.append("已批准提交但缺少墙生存报告 (reports/wall_survival.md)")
    return issues


GATES = {"G0": gate0, "G1": gate1, "G2": gate2, "G3": gate3}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", choices=sorted(GATES), help="只运行指定门")
    args = ap.parse_args()
    p = project_dir()
    all_ok = True
    for name, fn in GATES.items():
        if args.gate and name != args.gate:
            continue
        issues = fn(p)
        ok = not issues
        all_ok = all_ok and ok
        detail = "; ".join(issues) if issues else "ok"
        print(f"[{name}] {'PASS' if ok else 'FAIL'} - {detail}")
    print("ALL GATES: " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
