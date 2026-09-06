# -*- coding: utf-8 -*-
"""Fixed 11-step result analysis pipeline (pre-registered 2026-08-08).

Run mechanically when A1/S1/W1 results return. Does NOT interpret scores by
hand; it applies the locked decision table (registry/pre_registered_decisions.json)
and the equivalence band. pair_selector weights stay frozen.

Input JSON (--results):
{
  "w1_reps": [{"ref": "...", "status": "...", "public_score": null, "runtime_s": null}, ...],
  "a1":      {"ref": "...", "status": "...", "public_score": null, "runtime_s": null},
  "s1":      {"ref": "...", "status": "...", "public_score": null, "runtime_s": null},
  "n6b_score": 5.115,
  "historical_w1": 87.930
}

Usage (from project/):
  python scripts/result_analysis_pipeline.py --results registry/results_triangle.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "reports" / "new_routes_20260808"


def num(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    args = ap.parse_args()

    r = json.loads(pathlib.Path(args.results).read_text(encoding="utf-8-sig"))
    pre = json.loads((ROOT / "registry" / "pre_registered_decisions.json").read_text(encoding="utf-8"))
    band_floor = float(pre["practical_min_effect"])

    steps = []

    def step(name: str, detail: str) -> None:
        steps.append({"step": name, "detail": detail})
        print(f"[{len(steps):02d}] {name}: {detail}")

    # 1-3 checks
    reps = r.get("w1_reps", [])
    step("status_check", json.dumps([{x.get("ref"): x.get("status")} for x in reps]
                                    + [{"a1": r["a1"].get("status")}, {"s1": r["s1"].get("status")}],
                                    ensure_ascii=False))
    runtimes = {x["ref"]: x.get("runtime_s") for x in reps}
    runtimes.update({"a1": r["a1"].get("runtime_s"), "s1": r["s1"].get("runtime_s")})
    step("runtime_check", json.dumps(runtimes, ensure_ascii=False))
    errs = [x.get("ref") for x in reps if "ERROR" in str(x.get("status", "")).upper()]
    if "ERROR" in str(r["a1"].get("status", "")).upper():
        errs.append(r["a1"]["ref"])
    if "ERROR" in str(r["s1"].get("status", "")).upper():
        errs.append(r["s1"]["ref"])
    step("error_partial_check", f"ERROR refs={errs or 'none'}; partial-credit needs kernel log")

    # 4 W1 replicates
    w1a, w1b = num(reps[0].get("public_score")) if len(reps) > 0 else None, num(reps[1].get("public_score")) if len(reps) > 1 else None
    w1_scores = [x for x in (w1a, w1b) if x is not None]
    w1_mean = sum(w1_scores) / len(w1_scores) if w1_scores else None
    w1_range = max(w1_scores) - min(w1_scores) if len(w1_scores) >= 2 else None
    w1_mid = (w1a + w1b) / 2 if w1a is not None and w1b is not None else None
    step("w1_replicates", f"a={w1a} b={w1b} mean={w1_mean} range={w1_range} mid={w1_mid} (n=2: range=noise scale, 不算 SD)")

    # 5 normalization
    hist = num(r.get("historical_w1"))
    h = (w1_mean / hist) if w1_mean is not None and hist else None
    step("normalize_H", f"H = W1_mean/{hist} = {h if h is not None else 'n/a'}")

    # 6 equivalence band
    band = max(band_floor, w1_range or 0.0)
    a1_s, s1_s = num(r["a1"].get("public_score")), num(r["s1"].get("public_score"))
    n6b = num(r.get("n6b_score"))
    d_a = (a1_s - w1_mean) if a1_s is not None and w1_mean is not None else None
    d_s = (s1_s - n6b) if s1_s is not None and n6b is not None else None

    def verdict(d, pos, neg, none):
        if d is None:
            return "PENDING"
        if abs(d) <= band:
            return none
        return pos if d > 0 else neg

    v_a = verdict(d_a, "multi-post 升级 aggressive 主线", "kill A", "NO CLEAR EFFECT -> A 暂停")
    v_s = verdict(d_s, "CONFUSED 保留 hedge 身份（需 S1>10）",
                  "CONFUSED 降研究备份",
                  "NO CLEAR EFFECT -> CONFUSED 研究备份")
    if s1_s is not None and s1_s <= 10 and d_s is not None and d_s > band:
        v_s = "S1 个位数 -> CONFUSED 研究备份（不因正 ΔS 升级）"
    step("equivalence_band", f"band={band} (max(practical={band_floor}, W1_range={w1_range})) "
                             f"ΔA={d_a} -> {v_a}; ΔS={d_s} -> {v_s}")

    # 7-10 placeholders / mechanical next steps
    step("RS_GATE", "跑 returned_score_gate.py --ref <ref> --log <output> 后回填 E 可见信号")
    step("route_status_update", "按结果更新 registry/route_status.json（COMPLETE/ERROR/CONTROL）")
    step("pair_selector_update", "仅更新 route_matrix 的 observed 层（public/runtime/error），权重冻结不动")
    step("next_shot_decision", "只有当候选满足 DV + ceiling/hedge + G3 + 失败模式正交 才打 4/5 枪；否则留空")

    # 11 W1 branch
    if any("ERROR" in str(x.get("status", "")).upper() for x in reps):
        w1_branch = "任一 ERROR -> W1 非 deterministic control；reliability 升权"
    elif w1_range is not None and w1_range <= band:
        w1_branch = f"W1 接近（range={w1_range}≤band）-> W1_mean={w1_mean} 当 control"
    elif w1_range is not None:
        w1_branch = f"W1 差异大（range={w1_range}>band）-> 用区间基准，不点对点；必要时补第 3 control"
    else:
        w1_branch = "PENDING"
    step("w1_branch", w1_branch)

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "result_analysis_triangle.json"
    out.write_text(
        json.dumps(
            {"date": "2026-08-08", "inputs": r, "steps": steps,
             "band": band, "w1_mean": w1_mean, "w1_range": w1_range,
             "H": h, "delta_A": d_a, "delta_S": d_s,
             "verdict_A": v_a, "verdict_S": v_s, "w1_branch": w1_branch},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
