"""Build family-mixture contrast variants for online attribution (F010).

Design (2026-08-08 methodology note):
  Probe 1  D/C-heavy: direct 40 / decompose 40 / tool 10 / reframe 10
  Probe 2  D/T-heavy: direct 40 / decompose 10 / tool 40 / reframe 10
  Probe 3  D/R-heavy: direct 40 / decompose 10 / tool 10 / reframe 40
Balanced probe = variants/s5_router_pool.py (25/25/25/25, already built).

All variants: N=1250, k=1, globally unique recipients, pure CONFUSED,
private-safe (15-80%).  Only the family mix differs -> aggregate score deltas
can be attributed to C/T/R with D as the stable backbone.

Usage (from project/):
  python scripts/build_family_contrasts.py
"""

from __future__ import annotations

import json
from pathlib import Path

from build_s5_router import DOMAINS, FAMILIES, _to

ROOT = Path(__file__).resolve().parents[1]
TOTAL = 1250

MIXES = {
    "s5_dc_heavy": (40, 40, 10, 10),
    "s5_dt_heavy": (40, 10, 40, 10),
    "s5_dr_heavy": (40, 10, 10, 40),
}


def allocate(total: int, weights: tuple[int, ...]) -> list[int]:
    raw = [total * w / sum(weights) for w in weights]
    counts = [int(x) for x in raw]
    remainder = total - sum(counts)
    order = sorted(range(len(weights)), key=lambda i: raw[i] - counts[i], reverse=True)
    for j in range(remainder):
        counts[order[j % len(order)]] += 1
    return counts


def main() -> int:
    for variant_name, weights in MIXES.items():
        counts = allocate(TOTAL, weights)
        family_plan: list[int] = []
        for idx, n in enumerate(counts):
            family_plan.extend([idx] * n)
        msgs: list[str] = []
        meta: list[dict] = []
        for i, family_idx in enumerate(family_plan):
            family_key, template, tags = FAMILIES[family_idx]
            to = _to(i)
            msg = template.format(to=to).strip()
            msgs.append(msg)
            meta.append({
                "index": i,
                "family": family_key,
                "recipient": to,
                "chars": len(msg),
                **tags,
            })

        lines = [
            "from aicomp_sdk.attacks import AttackAlgorithmBase, AttackCandidate, AttackRunConfig",
            "",
            "",
            "class AttackAlgorithm(AttackAlgorithmBase):",
            "    def run(self, env, config=None):",
            "        return [AttackCandidate(user_messages=(m,)) for m in _CANDIDATES]",
            "",
            "",
            "_CANDIDATES = [",
        ]
        for m in msgs:
            lines.append("    %r," % m)
        lines.append("]")
        variant = ROOT / "variants" / f"{variant_name}.py"
        variant.write_text("\n".join(lines) + "\n", encoding="utf-8")

        mix = {FAMILIES[i][0]: weights[i] / 100.0 for i in range(len(weights))}
        counts_out = {FAMILIES[i][0]: counts[i] for i in range(len(counts))}
        meta_path = ROOT / "variants" / f"{variant_name}.meta.json"
        meta_path.write_text(json.dumps({
            "variant": variant.name,
            "total": TOTAL,
            "interactions": TOTAL,
            "k": 1,
            "family_mix": mix,
            "counts": counts_out,
            "candidates": meta,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {variant}  mix={mix} counts={counts_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
