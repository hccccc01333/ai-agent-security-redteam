# -*- coding: utf-8 -*-
"""RS-GATE v1: returned-score gate (2026-08-08).

Parses a submission's kernel Output / log text and gates the result:
  G1 fatal error present?            (format error / timeout / kaggle error)
  G2 public score vs thresholds      (--min-public default W1-3 = 84.93,
                                      --promote default W1 = 87.93)
  G3 real private rows present?      (fills E calibration)
  G4 A1 multi-post verdict           (max pf= across multi templates >= 2 -> GO A2)

Usage:
  python scripts/returned_score_gate.py --ref 55314000 --log path/to/output.txt
  Get-Content output.txt | python scripts/returned_score_gate.py --ref 55314000
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "reports" / "new_routes_20260808"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="?")
    ap.add_argument("--log", default=None, help="path to output text file")
    ap.add_argument("--min-public", type=float, default=None,
                    help="acceptable floor (W1_old 87.930 is ARCHIVED; pass explicitly if wanted)")
    ap.add_argument("--promote", type=float, default=None,
                    help="promotion line (W1_old archived; pass explicitly if wanted)")
    args = ap.parse_args()

    if args.log:
        text = pathlib.Path(args.log).read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()

    checks: list[dict] = []

    # G1 fatal errors
    error_markers = [
        "Submission Format Error",
        "Invalid Submission",
        "ModelEvaluationTimedOut",
        "GATEWAY_RAISED_EXCEPTION",
        "Kaggle Error",
        "system error",
    ]
    hits = [m for m in error_markers if m.lower() in text.lower()]
    fatal = bool(hits)
    checks.append(
        {
            "item": "G1_no_fatal_error",
            "status": "FAIL" if fatal else "PASS",
            "detail": ("found " + ", ".join(hits)) if hits else "no fatal markers",
        }
    )

    # G2 public score
    score = None
    m = re.search(r"\[GATEWAY\].*?gpt_oss_public\s*[=:]\s*([0-9.]+)", text, re.I)
    if not m:
        m = re.search(r"public\s*score\s*[=:]\s*([0-9.]+)", text, re.I)
    if not m:
        m = re.search(r"\[GATEWAY\][^\n]*?\b([0-9]+\.[0-9]+)\b", text, re.I)
    if m:
        score = float(m.group(1))
    if score is None:
        checks.append(
            {
                "item": "G2_public_score",
                "status": "WARN",
                "detail": "public score not parsed (check log format)",
            }
        )
    else:
        if args.min_public is None:
            status = "PASS"
            detail = f"public={score} (no threshold; W1_old archived)"
        else:
            status = "PASS" if score >= args.min_public else "FAIL"
            promote_note = ""
            if args.promote is not None:
                promote_note = " promoted" if score >= args.promote else ""
            detail = (
                f"public={score} min={args.min_public}"
                f"{' promote=' + str(args.promote) if args.promote is not None else ''}"
                f"{promote_note}"
            )
        checks.append(
            {
                "item": "G2_public_score",
                "status": status,
                "detail": detail,
            }
        )

    # G3 private rows present
    priv = re.findall(
        r"(?:gpt_oss_private|gemma_private)\s*[=:]\s*([0-9.]+)", text, re.I
    )
    checks.append(
        {
            "item": "G3_private_rows",
            "status": "PASS" if len(priv) >= 2 else "WARN",
            "detail": f"parsed private values={priv} (>=2 needed to fill E)",
        }
    )

    # G4 A1 multi-post verdict from template summary
    multi_stats = {}
    for tmpl, v, pf in re.findall(r"(\w+):v=(\d+)/pf=([\d.]+)", text):
        multi_stats[tmpl] = {"v": int(v), "pf": float(pf)}
    multi_max_pf = max(
        (s["pf"] for name, s in multi_stats.items() if name.startswith("multi_")),
        default=0.0,
    )
    verdict = "GO_A2" if multi_max_pf >= 2.0 else (
        "NO_MULTI" if "multi_" in "|".join(multi_stats) else "SUMMARY_MISSING"
    )
    checks.append(
        {
            "item": "G4_A1_multipost_verdict",
            "status": "PASS" if verdict == "GO_A2" else "WARN",
            "detail": f"max multi pf={multi_max_pf} stats={multi_stats} verdict={verdict}",
        }
    )

    fails = [c for c in checks if c["status"] == "FAIL"]
    warns = [c for c in checks if c["status"] == "WARN"]
    overall = "FAIL" if fails else ("WARN" if warns else "PASS")
    print(f"RS-GATE v1 ref={args.ref} overall={overall}")
    for c in checks:
        print(f"  [{c['status']}] {c['item']}: {c['detail']}")

    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"returned_score_gate_{args.ref}.json"
    out_path.write_text(
        json.dumps(
            {
                "date": "2026-08-08",
                "gate": "RS-GATE v1",
                "ref": args.ref,
                "overall": overall,
                "public_score": score,
                "private_values": priv,
                "multi_stats": multi_stats,
                "multi_verdict": verdict,
                "items": checks,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"WROTE {out_path}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
