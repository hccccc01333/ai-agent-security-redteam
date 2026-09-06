"""Frontis-MA1 / OpenMLE-Evo parent-utility adaptation for JED (Eq.4, App. C.4).

Paper (inference-time parent selection):
    U_i = lambda_s * s~_i + lambda_d * eDelta_i + lambda_n * nu_i
    P(i|I) = softmax(U_i / tau)
    defaults from OpenMLE-Evo source: score=1.0, delta=0.4, novelty=0.25,
    missing-valid-outcome penalty=2.0; min-max normalization.

JED adaptation (only locally available evidence; public LB is the sole true judge):
    - s~_i   : min-max normalized public score over the island (missing -> 0.0)
    - eDelta : positive public-score improvement over strongest parent / max delta
    - nu_i   : 1/sqrt(1 + earlier cards in the same bucket)
    - penalty: 2.0 when the local gate is not clean (any audit fail) -- the
               paper's "must be executable with a valid validation outcome"
               requirement, because a failed local gate is not a valid outcome.

Final submission selection is NOT sampled (paper C.4); this only ranks parents.

Usage (from project/):
  python scripts/parent_utility.py
  python scripts/parent_utility.py --bucket knob_probe --top 10
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "experiments.jsonl"

WEIGHTS = {"score": 1.0, "delta": 0.4, "novelty": 0.25}
GATE_PENALTY = 2.0


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def to_float(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def normalize_minmax(values: list[float | None]) -> list[float]:
    finite = [v for v in values if v is not None]
    if not finite:
        return [0.0 for _ in values]
    lo, hi = min(finite), max(finite)
    if hi - lo < 1e-12:
        return [0.5 if v is not None else 0.0 for v in values]
    return [0.0 if v is None else (v - lo) / (hi - lo) for v in values]


def normalize_positive_deltas(deltas: list[float]) -> list[float]:
    best = max([d for d in deltas if d > 0.0] or [0.0])
    if best <= 0.0:
        return [0.0 for _ in deltas]
    return [d / best if d > 0.0 else 0.0 for d in deltas]


def gate_is_clean(entry: dict) -> bool:
    audits = entry.get("audits") or {}
    for v in audits.values():
        s = str(v).lower()
        if s.startswith("fail") or s.startswith("error"):
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Frontis-MA1 parent utility (JED adaptation)")
    ap.add_argument("--bucket", default=None, help="restrict island to one bucket")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    entries = load_jsonl(REGISTRY)
    by_id = {e.get("experiment_id"): e for e in entries}

    # island: optionally one bucket; otherwise everything with a variant file
    island = [
        e
        for e in entries
        if e.get("variant_file")
        and (args.bucket is None or (e.get("bucket") or "unknown") == args.bucket)
    ]
    island.sort(key=lambda e: str(e.get("registered_at") or ""))

    scores: dict[str, float | None] = {
        e["experiment_id"]: to_float(e.get("metrics", {}).get("public_score"))
        for e in island
    }
    score_components = normalize_minmax([scores[e["experiment_id"]] for e in island])

    raw_deltas: list[float] = []
    for e in island:
        parent = by_id.get(e.get("parent_id") or "")
        child, par = scores[e["experiment_id"]], scores.get(e.get("parent_id") or "")
        if parent is None or child is None or par is None:
            raw_deltas.append(0.0)
        else:
            raw_deltas.append(max(0.0, child - par))
    delta_components = normalize_positive_deltas(raw_deltas)

    family_counts: dict[str, int] = {}
    rows = []
    for e, sc, dc, raw_delta in zip(island, score_components, delta_components, raw_deltas):
        family = e.get("bucket") or "unknown"
        seen_before = family_counts.get(family, 0)
        novelty = 1.0 / math.sqrt(1.0 + seen_before)
        family_counts[family] = seen_before + 1
        penalty = 0.0 if gate_is_clean(e) else GATE_PENALTY
        utility = (
            WEIGHTS["score"] * sc
            + WEIGHTS["delta"] * dc
            + WEIGHTS["novelty"] * novelty
            - penalty
        )
        rows.append(
            {
                "id": e["experiment_id"],
                "bucket": family,
                "score": scores[e["experiment_id"]],
                "score_c": round(sc, 3),
                "delta_c": round(dc, 3),
                "raw_delta": round(raw_delta, 3),
                "novelty_c": round(novelty, 3),
                "penalty": penalty,
                "utility": round(utility, 3),
                "status": e.get("decision", {}).get("status"),
            }
        )

    rows.sort(key=lambda r: r["utility"], reverse=True)
    utilities = [r["utility"] for r in rows]
    mx = max(utilities) if utilities else 0.0
    exp = [math.exp(u - mx) for u in utilities]
    total = sum(exp) or 1.0
    probs = [x / total for x in exp]
    for r, p in zip(rows, probs):
        r["prob"] = round(p, 4)

    header = f"{'id':<18}{'bucket':<14}{'score':>8}{'s_c':>6}{'d_c':>6}{'n_c':>6}{'pen':>5}{'U':>8}{'P':>8}  status"
    print(header)
    for r in rows[: args.top]:
        print(
            f"{r['id']:<18}{r['bucket']:<14}{str(r['score']):>8}{r['score_c']:>6}"
            f"{r['delta_c']:>6}{r['novelty_c']:>6}{r['penalty']:>5.1f}{r['utility']:>8.3f}"
            f"{r['prob']:>8.4f}  {r['status']}"
        )
    print(f"\nweights: {WEIGHTS}  gate_penalty={GATE_PENALTY}  island={len(rows)}"
          f"{' (bucket=' + args.bucket + ')' if args.bucket else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
