# -*- coding: utf-8 -*-
"""Final-two-submission pair selector (2026-08-08).

U(i,j) = sum_g p_g * max(S_ig, S_jg)   (uniform guardrail prior by default)
U_robust = 0.6*mean + 0.4*CVaR_25% over the pair-max guardrail vector.

Input: JSON file {routes: {name: {G0..G7: value}}} (per-candidate raw proxies
from P003 / probes are fine for relative ordering; mark 'unit' in the file).

Usage (from project/):
  python scripts/pair_selector.py --matrix reports/new_routes_20260808/route_matrix.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
TIER_ORDER = ["G0_allow_all", "G1_optimal", "G2_sink_dlp", "G3_all_args_dlp",
              "G4_decode_dlp", "G5_provenance", "G6_persistent_taint", "G7_deny_all"]


def cvarlow(vals: list[float], q: float = 0.25) -> float:
    s = sorted(vals)
    k = max(1, round(len(s) * q))
    return sum(s[:k]) / k


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--priors", default=None, help="JSON dict G-tier -> p (default uniform)")
    args = ap.parse_args()

    data = json.loads(pathlib.Path(args.matrix).read_text(encoding="utf-8"))
    routes = data["routes"]
    tiers = TIER_ORDER if not data.get("tiers") else data["tiers"]
    priors = {}
    if args.priors:
        priors = json.loads(pathlib.Path(args.priors).read_text(encoding="utf-8"))
    if not priors:
        priors = {t: 1.0 / len(tiers) for t in tiers}

    def vec(name: str) -> list[float]:
        return [float(routes[name].get(t, 0.0)) for t in tiers]

    results = []
    for a, b in itertools.combinations(sorted(routes), 2):
        va, vb = vec(a), vec(b)
        pair_max = [max(x, y) for x, y in zip(va, vb)]
        u = sum(priors[t] * m for t, m in zip(tiers, pair_max))
        robust = 0.6 * u + 0.4 * cvarlow(pair_max)
        results.append({"pair": f"{a}+{b}", "U_mean": round(u, 2),
                        "U_robust": round(robust, 2),
                        "pair_max": [round(v, 1) for v in pair_max]})

    results.sort(key=lambda r: -r["U_robust"])
    print(f"{'pair':<30} {'U_mean':>8} {'U_robust':>9}")
    for r in results[:10]:
        print(f"{r['pair']:<30} {r['U_mean']:>8} {r['U_robust']:>9}")

    out = ROOT.parent / "reports" / "new_routes_20260808" / "pair_ranking.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"date": "2026-08-08", "unit": data.get("unit", "?"),
             "priors": priors, "ranking": results},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
