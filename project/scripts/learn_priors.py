"""Minimal hybrid learning: derive family/template priors from real scores.

Reads registry/submission_manifest.json (family_mix, interactions, public_score)
and writes registry/template_priors.json with, per family:
  - submissions seen, mean public score, implied raw per interaction
    (score*200 / interactions), and a simple weighted prior.
The prior is used offline to order template banks in future W-series variants
(attack.py itself is stateless per run, so learning happens across submissions).

Usage (from project/):
  python scripts/learn_priors.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "submission_manifest.json"
OUT = ROOT / "registry" / "template_priors.json"


def main() -> int:
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fam: dict[str, dict] = {}
    for e in doc["entries"]:
        score = e.get("public_score")
        interactions = e.get("interactions")
        if score is None or not interactions:
            continue
        mix = e.get("family_mix") or {}
        raw_per_int = score * 200.0 / float(interactions)
        for family, share in mix.items():
            if not isinstance(share, (int, float)) or share <= 0:
                continue
            s = fam.setdefault(family, {"n": 0, "score_sum": 0.0, "raw_per_int_sum": 0.0})
            s["n"] += 1
            s["score_sum"] += score
            s["raw_per_int_sum"] += raw_per_int

    priors = {}
    for family, s in sorted(fam.items()):
        priors[family] = {
            "submissions": s["n"],
            "mean_score": round(s["score_sum"] / s["n"], 3),
            "mean_raw_per_interaction": round(s["raw_per_int_sum"] / s["n"], 3),
            "prior_weight": round(s["raw_per_int_sum"] / s["n"], 3),
        }
    OUT.write_text(json.dumps({
        "source": "submission_manifest.json (real public scores)",
        "note": "raw_per_interaction = public_score*200/interactions; prior_weight = same metric for ordering",
        "priors": priors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(priors, ensure_ascii=False, indent=1))
    print(f"saved {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
