"""Audit whether S5 family labels correspond to real strategy separation.

For each candidate in variants/s5_router_pool.py we compute a small feature
vector (length, step markers, tool mention, process framing, command density,
punctuation structure) and a char-bigram Jaccard distance.  We then compare
mean within-family distance vs mean between-family distance:
  between >> within  -> families are real strategy clusters;
  between ~= within  -> labels only, no true differentiation.

Usage (from project/):
  python scripts/family_separation_audit.py
"""

from __future__ import annotations

import ast
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMAND_VERBS = ("请", "把", "发给", "发送", "转交", "执行", "使用", "找到")


def bigrams(s: str) -> set[str]:
    return {s[i:i + 2] for i in range(len(s) - 1)}


def features(msg: str, meta: dict) -> list[float]:
    return [
        len(msg),
        float(meta.get("step_count", 1)),
        float("工具" in msg),
        float("第一步" in msg or "第二步" in msg),
        float("流程" in msg or "协作" in msg),
        float(sum(msg.count(v) for v in COMMAND_VERBS)),
        float(msg.count("，") + msg.count("；") + msg.count("：")),
    ]


def main() -> int:
    meta_path = ROOT / "variants" / "s5_router_pool.meta.json"
    variant_path = ROOT / "variants" / "s5_router_pool.py"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))["candidates"]
    src = variant_path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    assign = next(
        n for n in tree.body
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_CANDIDATES" for t in n.targets)
    )
    msgs = ast.literal_eval(assign.value)
    assert len(msgs) == len(meta)

    families: dict[str, list[int]] = {}
    for i, m in enumerate(meta):
        families.setdefault(m["family"], []).append(i)

    vecs = {i: features(msgs[i], meta[i]) for i in range(len(msgs))}
    bgs = {i: bigrams(msgs[i]) for i in range(len(msgs))}

    # Normalize feature vectors (per-dimension z-score).
    dims = len(next(iter(vecs.values())))
    means = [sum(vecs[i][d] for i in vecs) / len(vecs) for d in range(dims)]
    stds = []
    for d in range(dims):
        var = sum((vecs[i][d] - means[d]) ** 2 for i in vecs) / len(vecs)
        stds.append(var ** 0.5 or 1.0)
    norm = {i: [(vecs[i][d] - means[d]) / stds[d] for d in range(dims)] for i in vecs}

    def vec_dist(a: int, b: int) -> float:
        return sum((norm[a][d] - norm[b][d]) ** 2 for d in range(dims)) ** 0.5

    def jac_dist(a: int, b: int) -> float:
        u, v = bgs[a], bgs[b]
        if not u or not v:
            return 1.0
        return 1.0 - len(u & v) / len(u | v)

    rng = random.Random(42)
    sample = {fam: rng.sample(idx, min(150, len(idx))) for fam, idx in families.items()}
    pairs = [(f1, f2) for f1, f2 in itertools.combinations_with_replacement(families, 2)]
    stats: dict[str, dict] = {}
    for f1, f2 in pairs:
        acc_v, acc_j, n = 0.0, 0.0, 0
        for a in sample[f1]:
            for b in sample[f2]:
                if f1 == f2 and a >= b:
                    continue
                acc_v += vec_dist(a, b)
                acc_j += jac_dist(a, b)
                n += 1
        stats[f"{f1}~{f2}"] = {"n": n, "vec_dist": round(acc_v / n, 4),
                               "jac_dist": round(acc_j / n, 4)}

    within = [s["vec_dist"] for k, s in stats.items() if k.split("~")[0] == k.split("~")[1]]
    between = [s["vec_dist"] for k, s in stats.items() if k.split("~")[0] != k.split("~")[1]]
    within_j = [s["jac_dist"] for k, s in stats.items() if k.split("~")[0] == k.split("~")[1]]
    between_j = [s["jac_dist"] for k, s in stats.items() if k.split("~")[0] != k.split("~")[1]]
    w, b = sum(within) / len(within), sum(between) / len(between)
    wj, bj = sum(within_j) / len(within_j), sum(between_j) / len(between_j)
    result = {
        "timestamp": "2026-08-08",
        "variant": "s5_router_pool.py",
        "sample_per_family": 150,
        "pairwise": stats,
        "feature_vector": {"within_mean": round(w, 4), "between_mean": round(b, 4),
                           "separation_ratio": round(b / w, 3)},
        "bigram_jaccard": {"within_mean": round(wj, 4), "between_mean": round(bj, 4),
                           "separation_ratio": round(bj / wj, 3)},
        "verdict": "SEPARATED" if b / w > 1.2 and bj / wj > 1.1 else "LABELS_ONLY",
    }
    out = ROOT / "registry" / "family_separation_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
