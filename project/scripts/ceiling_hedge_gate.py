# -*- coding: utf-8 -*-
"""Ceiling / Hedge Gate (2026-08-08, user refinement).

Two tracks, not one threshold:
  - aggressive: theoretical ceiling (100% conversion, two-row mean) >= target
    (default 90). Below that, do not chase high score on this route.
  - hedge: robust floor under worst/second-worst guardrail scenarios must
    clearly beat the current hedge floor. Low ceiling is allowed.

Usage (from project/):
  python scripts/ceiling_hedge_gate.py --track aggressive --route W1 --ceiling 91.6
  python scripts/ceiling_hedge_gate.py --track hedge --route CONFUSED --floor 20 ^
      --current-hedge-floor 5 --worst-g G7 --second-worst-g G6
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
    ap.add_argument("--track", choices=["aggressive", "hedge"], required=True)
    ap.add_argument("--route", required=True)
    ap.add_argument("--ceiling", type=float, default=None, help="aggressive track")
    ap.add_argument("--target", type=float, default=90.0, help="aggressive target line")
    ap.add_argument("--floor", type=float, default=None, help="hedge track robust floor")
    ap.add_argument("--current-hedge-floor", type=float, default=0.0)
    ap.add_argument("--worst-g", default="G7")
    ap.add_argument("--second-worst-g", default="G6")
    args = ap.parse_args()

    if args.track == "aggressive":
        if args.ceiling is None:
            print("FAIL aggressive track requires --ceiling")
            return 2
        ok = args.ceiling >= args.target
        detail = f"ceiling={args.ceiling} target={args.target} -> {'PASS' if ok else 'NO-GO (not a 90-120 route)'}"
    else:
        if args.floor is None:
            print("FAIL hedge track requires --floor")
            return 2
        ok = args.floor > args.current_hedge_floor
        detail = (
            f"floor@{args.worst_g}/{args.second_worst_g}={args.floor} "
            f"current_hedge_floor={args.current_hedge_floor} -> "
            f"{'PASS (keep hedge)' if ok else 'NO-GO (hedge not clearly better)'}"
        )

    print(f"[{'PASS' if ok else 'FAIL'}] ceiling_hedge track={args.track} route={args.route}: {detail}")
    REGISTRY.mkdir(parents=True, exist_ok=True)
    with (REGISTRY / "ceiling_hedge_runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "track": args.track,
                    "route": args.route,
                    "ceiling": args.ceiling,
                    "target": args.target,
                    "floor": args.floor,
                    "current_hedge_floor": args.current_hedge_floor,
                    "worst_g": args.worst_g,
                    "second_worst_g": args.second_worst_g,
                    "gate": "PASS" if ok else "FAIL",
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    print("logged registry/ceiling_hedge_runs.jsonl")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
