# -*- coding: utf-8 -*-
"""G7-DV: Decision Value Gate (2026-08-08, user refinement).

NOT "answer at least two questions". The gate asks: would this shot change a
later decision? If every possible outcome maps to the same decision, the shot
has zero decision value and must not be submitted.

Usage (from project/):
  python scripts/decision_value_gate.py --shot W1_clean --unknown "new harness baseline" ^
      --outcomes '[{"result":"W1_new ~ old","decision":"harness stable; keep old refs"},{"result":"W1_new much lower","decision":"renormalize all routes"},{"result":"ERROR again","decision":"W1 not a control; switch baseline"}]'
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", required=True)
    ap.add_argument("--unknown", required=True, help="what we currently don't know")
    ap.add_argument("--outcomes", default=None, help="JSON list of {result, decision}")
    ap.add_argument("--outcomes-file", default=None, help="path to JSON file with the list")
    args = ap.parse_args()

    if args.outcomes_file:
        outcomes = json.loads(pathlib.Path(args.outcomes_file).read_text(encoding="utf-8"))
    else:
        try:
            outcomes = json.loads(args.outcomes)
        except json.JSONDecodeError as e:
            print(f"FAIL outcomes JSON invalid: {e}")
            return 2
    if not isinstance(outcomes, list) or len(outcomes) < 2:
        print("FAIL need >= 2 outcomes")
        return 2

    decisions = [str(o.get("decision", "")).strip() for o in outcomes]
    distinct = sorted(set(decisions))
    ok = len(distinct) >= 2 and all(d for d in decisions)
    print(f"[{'PASS' if ok else 'FAIL'}] G7-DV shot={args.shot}")
    print(f"  unknown: {args.unknown}")
    for o in outcomes:
        print(f"    outcome: {o.get('result')} -> {o.get('decision')}")
    print(f"  distinct decisions: {len(distinct)} (need >=2)")

    REGISTRY.mkdir(parents=True, exist_ok=True)
    with (REGISTRY / "decision_value_runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "shot": args.shot,
                    "unknown": args.unknown,
                    "outcomes": outcomes,
                    "distinct_decisions": distinct,
                    "gate": "PASS" if ok else "FAIL",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    print("logged registry/decision_value_runs.jsonl")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
