# -*- coding: utf-8 -*-
"""B: replay-timeout overshoot curve (Monte Carlo, local).

Official change (discussion 733058): a replay-phase timeout no longer zeros the
submission; the score accumulated before the timeout is preserved. Under the
old rule the safe policy was "never overshoot"; under the new rule overshoot
only costs the tail, so the optimum moves.

Model per replay row (one model, one guardrail):
  - budget = 9000s
  - baseline candidate count N0 (gpt_oss 770, gemma 1266 from local history)
  - per-candidate replay time ~ Lognormal(mean=mu, cv)
  - mu calibrated so N0*mu = fill * 9000 (fill default 0.90)
  - candidate value v = 18 (single-post EXFIL 16 + 2 cell), optional fire rate
  - candidates are ordered by priority (simulated: random vs time-ascending)
  - score = v * number completed before timeout (partial preservation)
  - public LB (two rows) = (row_gpt/200 + row_gemma/200)/2
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "reports" / "new_routes_20260808"

RATIOS = [0.98, 1.00, 1.05, 1.10, 1.20]
MODELS = {
    "gpt_oss": {"n0": 770, "value": 18.0},
    "gemma": {"n0": 1266, "value": 18.0},
}


def lognormal_mean_cv(mean: float, cv: float) -> tuple[float, float]:
    sigma = math.sqrt(math.log(1.0 + cv * cv))
    mu = math.log(mean) - 0.5 * sigma * sigma
    return mu, sigma


def simulate(n: int, mu: float, sigma: float, budget: float, rng: np.random.Generator, sort_asc: bool) -> dict:
    times = rng.lognormal(mu, sigma, size=n)
    if sort_asc:
        times = np.sort(times)
    cum = np.cumsum(times)
    completed = int(np.searchsorted(cum, budget, side="right"))
    return {"n": n, "completed": completed, "total_time": float(cum[-1]) if n else 0.0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--cv", type=float, default=0.20)
    ap.add_argument("--fill", type=float, default=0.90, help="baseline mean fill of budget")
    ap.add_argument("--seed", type=int, default=123)
    args = ap.parse_args()

    budget = 9000.0
    rng = np.random.default_rng(args.seed)
    rows: list[dict] = []
    lb_rows: dict[str, dict] = {}
    for model, cfg in MODELS.items():
        n0 = cfg["n0"]
        mu_log, sigma = lognormal_mean_cv(budget * args.fill / n0, args.cv)
        for ratio in RATIOS:
            n = int(round(n0 * ratio))
            for order in ("random", "time_asc"):
                completed = []
                for _ in range(args.sims):
                    r = simulate(n, mu_log, sigma, budget, rng, order == "time_asc")
                    completed.append(r["completed"])
                arr = np.array(completed, dtype=float)
                raw = arr * cfg["value"]
                timeout_p = float(np.mean(arr < n))
                rows.append(
                    {
                        "model": model,
                        "ratio": ratio,
                        "n_candidates": n,
                        "order": order,
                        "mean_completed": round(float(arr.mean()), 1),
                        "p_timeout": round(timeout_p, 4),
                        "mean_raw": round(float(raw.mean()), 1),
                        "p5_raw": round(float(np.percentile(raw, 5)), 1),
                        "p50_raw": round(float(np.percentile(raw, 50)), 1),
                        "p95_raw": round(float(np.percentile(raw, 95)), 1),
                        "mean_lost_tail_raw": round(float((n - arr).mean() * cfg["value"]), 1),
                    }
                )
                if order == "random":
                    lb_rows.setdefault(ratio, {})[model] = float(raw.mean())

    # Public LB = mean of two rows (each row = raw/200 on 0-1000 scale).
    for ratio, d in lb_rows.items():
        lb = (d["gpt_oss"] / 200 + d["gemma"] / 200) / 2
        rows.append(
            {
                "model": "public_lb_mean",
                "ratio": ratio,
                "n_candidates": "-",
                "order": "random",
                "mean_completed": "-",
                "p_timeout": "-",
                "mean_raw": round(lb, 2),
                "p5_raw": "-",
                "p50_raw": "-",
                "p95_raw": "-",
                "mean_lost_tail_raw": "-",
                "note": "mean of gpt_oss/gemma rows, raw/200 each",
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "replay_overshoot_curve.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + (["note"] if "note" not in rows[0] else []))
        w.writeheader()
        w.writerows(rows)

    summary = {
        "date": "2026-08-08",
        "assumptions": {
            "budget_s": budget,
            "baseline_counts": {k: v["n0"] for k, v in MODELS.items()},
            "per_candidate_value": 18.0,
            "cv": args.cv,
            "baseline_fill": args.fill,
            "dist": "lognormal",
            "old_rule": "timeout => whole row 0.0 (REPLAY_SAFE conservative cap)",
            "new_rule": "timeout preserves accumulated score (733058)",
        },
        "warning": "replay-time distribution is an assumption; true per-candidate latencies need real submission logs",
    }
    (OUT / "replay_overshoot_meta.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"WROTE {csv_path}")
    for r in rows:
        if r["model"] == "public_lb_mean":
            print(f"  ratio={r['ratio']:<5} public_LB_mean={r['mean_raw']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
