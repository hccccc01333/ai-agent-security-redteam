"""Round judge: applies the W1 judgment line after sync_submissions.py.

Reads the registry and reports, for every in-flight 2026-08-02 submission that
has a public score, the verdict vs its parent; then applies the W1 line:
    W1 >= 87.795 (>= 87.8) -> knob_probe same axis, new candidate must pass
                               the 3-salt mock gate (EXP-013: REPS=8 + FIRE<=0.6
                               or a new higher-fire template)
    W1 <  87.795            -> back to Q5, switch bucket (user direction or
                               an info-experiment candidate)

Usage (from project/):
  python scripts/sync_submissions.py
  python scripts/judge_round.py

Exit codes: 0 = W1 still pending; 1 = W1 scored and the judgment line fired.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "experiments.jsonl"

W1_LINE = 87.795  # Q5 anchor; >=87.8 same-axis
IN_FLIGHT = {
    "w1_probe5_fire65": "W1 (probe5/fire0.65)",
    "x2_tld_com": "X2 (.co->.com)",
    "x3_tiebreak_fire": "X3 (tiebreak)",
    "x4_https": "X4 (http->https)",
    "x5_plain_via": "X5 (plain wording)",
}


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


def resolve(entries: list[dict], ref: str) -> dict | None:
    rl = ref.lower()
    for e in entries:
        if e.get("experiment_id", "").lower() == rl:
            return e
    for e in entries:
        if Path(e.get("variant_file", "")).stem.lower() == rl:
            return e
    return None


def main() -> int:
    entries = load_jsonl(REGISTRY)
    by_id = {e.get("experiment_id"): e for e in entries}
    w1 = by_id.get("w1_probe5_fire65")
    w1_score = (w1 or {}).get("metrics", {}).get("public_score")

    print("=== 本轮判线（2026-08-02 五枪）===")
    for eid, label in IN_FLIGHT.items():
        e = by_id.get(eid)
        if not e:
            print(f"  {label:<24} 未注册")
            continue
        score = e.get("metrics", {}).get("public_score")
        if score is None:
            print(f"  {label:<24} PENDING（未出分）")
            continue
        parent = resolve(entries, e.get("parent_id")) if e.get("parent_id") else None
        pscore = (parent or {}).get("metrics", {}).get("public_score")
        verdict = "promoted" if pscore is not None and float(score) >= float(pscore) else "rejected"
        print(f"  {label:<24} {score} vs 父 {pscore} -> {verdict}")

    if w1_score is None:
        print("\n判定：W1 未出分，等待中。")
        return 0

    w1f = float(w1_score)
    if w1f >= W1_LINE:
        print(
            f"\n判定：W1 = {w1f} >= {W1_LINE} -> knob_probe 同轴。"
            "\n下一刀候选（须先过 3 盐 mock，EXP-013）："
            "\n  1) PROBE_REPS=8 + MIN_FIRE<=0.6（mock 稳定带）"
            "\n  2) 用户提供真成交率显著 >0.65 的新模板"
        )
    else:
        print(
            f"\n判定：W1 = {w1f} < {W1_LINE} -> 回 Q5 换桶。"
            "\n下一步：等用户给新方向，或从排队信息实验中选（pred_exfil 已冻结 EXP-010）。"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
