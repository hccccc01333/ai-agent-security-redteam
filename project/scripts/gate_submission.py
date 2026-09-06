"""Unified submission gate (G3) — one command, all gates, one verdict.

Blocks submission unless EVERY blocking gate passes:
  1. validate_submission        (AST + AttackAlgorithm contract + no forbidden features)
  2. evaluate_candidate --mock  (ast/no_op/smoke_allow + smoke_optimal x2 + 3-salt selection mock)
  3. local_score_gate latency=0 (numeric mock-replay score vs baseline; threshold ratio)
  4. sizing sanity (only when REPLAY_SAFE changed): fake-latency run, threshold ratio
  5. wall survival 300s         (smoke_test --budget-s 300 --guardrail optimal)
  6. guardrail ladder           (INFORMATIONAL: family risk class from guardrail_family_scan JSON)

Writes a per-variant report to reports/gate_<stem>.md and a machine-readable row
to registry/gate_runs.jsonl.  Exit 0 = all blocking gates PASS.

Usage (from project/):
  python scripts/gate_submission.py --variant variants/n9_w1_small.py
  python scripts/gate_submission.py --variant variants/n6b_confused_large.py --baseline variants/n6_confused_hedge.py
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT.parent / "reports"
REGISTRY = ROOT / "registry"
LANTERN = ROOT / "registry" / "guardrail_family_scan_2026-08-07.json"


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 1200) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def summary(res: subprocess.CompletedProcess, n: int = 4) -> str:
    out = (res.stdout or "").strip().splitlines()
    err = (res.stderr or "").strip().splitlines()
    lines = (out + ["stderr:"] + err if err else out)[-n:]
    return " | ".join(lines)


def read_replay_safe(path: Path) -> float | None:
    src = path.read_text(encoding="utf-8")
    m = re.search(r"^REPLAY_SAFE\s*=\s*([0-9.]+)", src, re.MULTILINE)
    return float(m.group(1)) if m else None


def ladder_report(src: str) -> dict:
    """Classify the variant's primary family from source heuristics + scan JSON."""
    info = {"family": "unknown", "risk_class": "?", "first_deny_tier": "?", "note": ""}
    if not LANTERN.exists():
        info["note"] = "ladder JSON missing"
        return info
    matrix = json.loads(LANTERN.read_text(encoding="utf-8"))
    families = {f["family"]: f for f in matrix.get("families", [])}
    is_cd = ("HEDGE_TEMPLATES" in src or "email.send" in src) and "http.post" not in src
    has_exfil = "http.post" in src and "SECRET_MARKER" in src
    family = "cd_email_clean" if is_cd else ("exfil_plain" if has_exfil else "unknown")
    f = families.get(family)
    if f:
        info.update(
            family=family,
            risk_class=f.get("risk_class", "?"),
            first_deny_tier=f.get("first_deny_tier", "?"),
            g1_raw=f.get("tiers", {}).get("G1_optimal", {}).get("raw"),
            g2_raw=f.get("tiers", {}).get("G2_sink_dlp", {}).get("raw"),
        )
        if family == "cd_email_clean":
            info["note"] = "hedge 通道：护栏梯子存活至 G6，仅 G7 全拒拦截（私榜保险）"
        else:
            info["note"] = "EXFIL 主攻：G1 计分但 G2（data 明文 DLP）即灭；私榜风险高，定位公榜冲分"
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified G3 submission gate")
    ap.add_argument("--variant", required=True)
    ap.add_argument("--baseline", default=None,
                    help="default: w1 for EXFIL, n6_confused_hedge for CD-only")
    ap.add_argument("--budget-s", type=float, default=300.0)
    ap.add_argument("--score-threshold", type=float, default=0.7)
    ap.add_argument("--no-wall", action="store_true")
    ap.add_argument("--json-out", action="store_true")
    args = ap.parse_args()

    variant = Path(args.variant)
    if not variant.is_absolute():
        variant = ROOT / variant
    if not variant.exists():
        print(f"FAIL variant not found: {variant}", file=sys.stderr)
        return 2

    src = variant.read_text(encoding="utf-8")
    is_cd_only = ("HEDGE_TEMPLATES" in src or "email.send" in src) and "http.post" not in src
    baseline = Path(args.baseline) if args.baseline else (
        ROOT / "variants" / ("n6_confused_hedge.py" if is_cd_only else "w1_probe5_fire65.py")
    )
    if not baseline.is_absolute():
        baseline = ROOT / baseline

    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str, blocking: bool = True) -> None:
        checks.append({"gate": name, "ok": bool(ok), "detail": detail, "blocking": blocking})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}" + ("" if blocking else "  (info)"))

    # 1. contract validation
    r = run([sys.executable, str(ROOT / "scripts" / "validate_submission.py"), "--variant", str(variant)])
    add("validate_submission", r.returncode == 0, summary(r))

    # 2. full evaluate_candidate (ast/no_op/smoke x3 + 3-salt selection mock)
    r = run([sys.executable, str(ROOT / "scripts" / "evaluate_candidate.py"),
             "--variant", str(variant), "--parent", str(baseline),
             "--bucket", "gate", "--hypothesis", f"unified gate run {datetime.now(timezone.utc):%Y-%m-%dT%H:%M}",
             "--mock", "--copy-attack"], timeout=600)
    add("evaluate_candidate(mock)", r.returncode == 0, summary(r, 2))

    # 3. local numeric score gate (latency=0 regression)
    r = run([sys.executable, str(ROOT / "scripts" / "local_score_gate.py"),
             "--variant", str(variant), "--baseline", str(baseline),
             "--candidates", "400", "--threshold", str(args.score_threshold)], timeout=600)
    score_ok = r.returncode == 0
    add("local_score(regression)", score_ok, summary(r, 3))

    # 4. sizing sanity when REPLAY_SAFE changed
    v_safe, b_safe = read_replay_safe(variant), read_replay_safe(baseline)
    if v_safe is not None and b_safe is not None and abs(v_safe - b_safe) > 1e-9:
        r = run([sys.executable, str(ROOT / "scripts" / "local_score_gate.py"),
                 "--variant", str(variant), "--baseline", str(baseline),
                 "--candidates", "2000", "--budget-s", "360000", "--latency", "30",
                 "--threshold", str(args.score_threshold)], timeout=600)
        add(f"local_score(sizing safe={v_safe} vs {b_safe})", r.returncode == 0, summary(r, 3))
    else:
        add("local_score(sizing)", True, "REPLAY_SAFE unchanged — skipped", blocking=False)

    # 5. wall survival
    if args.no_wall:
        add("wall_survival(300s)", True, "skipped (--no-wall)", blocking=False)
    else:
        attack_py = ROOT / "attack.py"
        backup = attack_py.read_bytes() if attack_py.exists() else None
        try:
            shutil.copy2(variant, attack_py)
            r = run([sys.executable, str(ROOT / "scripts" / "smoke_test.py"),
                     "--budget-s", str(args.budget_s), "--guardrail", "optimal"], timeout=600)
        finally:
            if backup is not None:
                attack_py.write_bytes(backup)
        add(f"wall_survival({args.budget_s:g}s)", r.returncode == 0, summary(r, 2))

    # 6. guardrail ladder (informational)
    ladder = ladder_report(src)
    add("guardrail_ladder", True,
        f"family={ladder.get('family')} risk={ladder.get('risk_class')} "
        f"first_deny={ladder.get('first_deny_tier')} note={ladder.get('note', '')}",
        blocking=False)

    blocking_fail = [c for c in checks if c["blocking"] and not c["ok"]]
    ok_all = not blocking_fail
    print(f"\nGATE VERDICT: {'PASS' if ok_all else 'FAIL'}")
    if blocking_fail:
        for c in blocking_fail:
            print(f"  blocked by {c['gate']}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = REPORTS / f"gate_{variant.stem}.md"
    lines = [
        f"# Gate report — {variant.stem}",
        "",
        f"- time: {stamp}",
        f"- baseline: {baseline.name}",
        f"- verdict: {'PASS' if ok_all else 'FAIL'}",
        "",
        "| gate | result | detail |",
        "|------|--------|--------|",
    ]
    for c in checks:
        lines.append(f"| {c['gate']} | {'PASS' if c['ok'] else 'FAIL'} | {c['detail'].replace('|', '/')[:140]} |")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"report: {report}")

    REGISTRY.mkdir(parents=True, exist_ok=True)
    with (REGISTRY / "gate_runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": stamp, "variant": variant.name, "baseline": baseline.name,
            "verdict": "PASS" if ok_all else "FAIL", "checks": checks,
        }, ensure_ascii=False) + "\n")

    if args.json_out:
        print(json.dumps({"verdict": "PASS" if ok_all else "FAIL", "checks": checks,
                          "ladder": ladder}, ensure_ascii=False))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
