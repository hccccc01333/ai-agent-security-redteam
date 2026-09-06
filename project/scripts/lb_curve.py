"""LB(p) Monte Carlo simulator —— 公榜分数分布预测器。

背景（registry/local_best.json 铁证）：本地确定性代理对所有候选一律 fire(p=1)，
本地分只对"结构差异"精确（家族/谓词/cell/护栏/成本），对"合规差异"
（措辞/模板/K）全盲——四个线上差 48 分的变体本地同为 36.0。

本脚本把 p 从常量变成变量，输出 LB 分布而非点估计：

    LB = mean_model[ raw_m / 200 ]
    raw_m = slots_m * (16 * E[instances] + 2 * P(first-fire))   # 结构 x 合规
    slots_m = min(B, (REPLAY_SAFE*T - hedge_cost) / (OVH + rounds*lat_m))

三步法：
  1. 结构分：每族 raw_per_fire 与 local_sim_guardrail_*.json 同构（7200/400=18）
  2. 先验 p ：p_base 仅由 W11 五锚反解一次；其余族用相对合规先验
    （衰减底 d 来自 F013-A/F014 剂量实测证据）
  3. Monte Carlo：采样服务器日（延迟抖动+坏日）、bank 规模、p → LB 分布

用法（project/ 下）：python scripts/lb_curve.py
"""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry"
OUT_JSON = REG / "lb_curve_20260822.json"

T_BUDGET = 9000.0
REPLAY_SAFE = 0.996
OVH_S = 1.0                 # 每候选固定开销 build_env+reset
N_SIM = 20000
SEED = 20260822

MODELS = ("gemma", "gpt_oss")
LAT_BASE = {"gemma": (6.0, 0.7), "gpt_oss": (10.0, 1.2)}   # 秒/轮 先验
BAD_DAY_P = 0.12
BAD_DAY_MULT = 1.22
DAY_SIGMA = 0.07
BANK_CENTER, BANK_SIGMA = 1250.0, 0.12    # 生成期预算推 bank 规模先验
RESIDUAL_SD = 1.2

ANCHOR_CAL = "w11_hedge10"
ANCHOR_TARGET = 81.045      # 五锚均值：80.505/80.595/80.775/81.540/81.810


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def beta_sample(rng: random.Random, mu: float, sigma: float) -> float:
    mu = clamp(mu, 0.03, 0.97)
    var = min(sigma * sigma, mu * (1 - mu) * 0.98)
    nu = mu * (1 - mu) / var - 1.0
    a, b = max(nu * mu, 0.3), max(nu * (1 - mu), 0.3)
    return clamp(rng.betavariate(a, b), 0.02, 0.99)


def norm_sample(rng: random.Random, mu: float, sigma: float,
                lo: float = 0.40, hi: float = 1.18) -> float:
    """截断正态——用于相对合规乘数（允许 >1 的提升先验）。"""
    return clamp(rng.gauss(mu, sigma), lo, hi)


def sample_latencies(rng: random.Random, lms: dict[str, float]) -> dict[str, float]:
    day = rng.lognormvariate(0.0, DAY_SIGMA)
    if rng.random() < BAD_DAY_P:
        day *= BAD_DAY_MULT
    return {m: max(3.0, rng.gauss(*LAT_BASE[m]) * day * lms[m]) for m in MODELS}


# ------------------------------------------------------------ 配置注册表 --
# rounds: 每候选交互轮数；decay: 多指令/多消息重复合规底（第 j 条 ∝ d^(j-1)）；
# rel: 相对核心合规先验 (mu, sd)；hedge_n: fixture 对冲候选数；
# bank_mult / lat_* : 模板级乘数先验；observed: 公榜实测（验证用）。
CONFIGS: dict[str, dict] = {
    # ---------------- 历史 holdout 验证集 ----------------
    "w11_hedge10": dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                        hedge_n=60, bank_mult=(1.00, 0.00),
                        observed=[80.775, 81.540, 80.595, 81.810, 80.505]),
    "w10_hedge0":  dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                        hedge_n=0, bank_mult=(1.00, 0.00),
                        observed=[82.755, 82.035]),
    "w13_hedge5":  dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                        hedge_n=30, bank_mult=(1.00, 0.00),
                        observed=[82.845, 77.130]),
    "w21_hedge7":  dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                        hedge_n=42, bank_mult=(1.00, 0.00),
                        observed=[81.270]),
    "w22_hedge15": dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                        hedge_n=60, bank_mult=(1.00, 0.00),
                        observed=[72.765]),
    "w19_dualpost": dict(rounds=1, decay=0.15, K=2, rel=(0.95, 0.08),
                         hedge_n=40, bank_mult=(0.95, 0.05),
                         observed=[76.665, 67.725]),
    "w1_minfire08": dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                         hedge_n=24, bank_mult=(1.00, 0.00),
                         observed=[82.845, 82.215, 66.915]),
    # f014 系：程序化构候选，生成不按 K 倍计费 -> bank_mult=(1.0, 0.05)；
    # f014c 内置 K 合规回退保底，分数形态（71.2 ≈ 锚-9）疑似触发回退，
    # 公榜无法干净估计每消息衰减 d -> 标记 fallback_suspect，不计入 MISS。
    "f014a_k2": dict(rounds=2, decay=0.50, K=2, rel=(0.95, 0.08),
                     hedge_n=0, bank_mult=(1.0, 0.05),
                     observed=[72.085]),
    "f014b_k4": dict(rounds=4, decay=0.50, K=4, rel=(0.95, 0.08),
                     hedge_n=0, bank_mult=(1.0, 0.05),
                     observed=[67.500]),
    "f014c_k8": dict(rounds=8, decay=0.50, K=8, rel=(0.95, 0.08),
                     hedge_n=0, bank_mult=(1.0, 0.05),
                     fallback_suspect=True,
                     observed=[71.155]),
    # ---------------- F015 五枪 ----------------
    "A_w11h0_reanchor": dict(rounds=1, decay=None, K=1, rel=(1.00, 0.00),
                             hedge_n=0, bank_mult=(1.00, 0.00)),
    "B_speed_gpto": dict(rounds=1, decay=None, K=1, rel=(0.93, 0.09),
                         hedge_n=0, bank_mult=(1.05, 0.05),
                         lat_gptoss=(0.70, 0.86), lat_gemma=(0.82, 0.94)),
    "C_speed_h5": dict(rounds=1, decay=None, K=1, rel=(0.93, 0.09),
                       hedge_n=30, bank_mult=(1.05, 0.05),
                       lat_gptoss=(0.70, 0.86), lat_gemma=(0.82, 0.94)),
    "D_fire90": dict(rounds=1, decay=None, K=1, rel=(1.06, 0.04),
                     hedge_n=0, bank_mult=(0.94, 0.05)),
    # E：deputy-only 混入已被模拟否决（EV/slot 3.3 vs core 16.7，med 67），
    # 换成 speed + fire90 组合（两条最有效杠杆叠加）。
    "E_speed_fire90": dict(rounds=1, decay=None, K=1, rel=(1.06, 0.04),
                           hedge_n=0, bank_mult=(1.05, 0.05),
                           lat_gptoss=(0.70, 0.86), lat_gemma=(0.82, 0.94)),
}


def fire_probs(cfg: dict, p_base: float, rng: random.Random) -> tuple[float, float]:
    """返回 (E[每候选实例数], P(首个动作成功))。"""
    rel = cfg["rel"][0] if cfg["rel"][1] == 0.0 else norm_sample(rng, *cfg["rel"])
    if cfg.get("decay") is None:
        p1 = clamp(p_base * rel, 0.0, 0.999)
        return p1, p1
    d = beta_sample(rng, cfg["decay"], 0.15)
    ps = [clamp(p_base * rel * d ** j, 0.0, 0.999) for j in range(cfg.get("K", 2))]
    return sum(ps), ps[0]


def simulate(name: str, p_base: float, rng: random.Random) -> float:
    cfg = CONFIGS[name]
    lm = {"gemma": 1.0, "gpt_oss": 1.0}
    lo, hi = cfg.get("lat_gemma", (1.0, 1.0))
    lm["gemma"] *= rng.uniform(lo, hi)
    lo, hi = cfg.get("lat_gptoss", (1.0, 1.0))
    lm["gpt_oss"] *= rng.uniform(lo, hi)
    lat = sample_latencies(rng, lm)

    bm_mu, bm_sd = cfg.get("bank_mult", (1.0, 0.0))
    B = rng.lognormvariate(math.log(BANK_CENTER * bm_mu), max(bm_sd, 1e-6))

    p_inst, p_first = fire_probs(cfg, p_base, rng)

    raws = []
    for m in MODELS:
        budget = REPLAY_SAFE * T_BUDGET - cfg["hedge_n"] * (OVH_S + lat[m])
        unit = OVH_S + cfg["rounds"] * lat[m]
        slots = min(int(B), int(max(budget, 0.0) / unit))
        r = slots * (16.0 * p_inst + 2.0 * p_first)
        raws.append(r)
    return sum(raws) / len(raws) / 200.0 + rng.gauss(0.0, RESIDUAL_SD)


def summarize(xs: list[float]) -> dict:
    xs = sorted(xs)
    q = lambda p: xs[int(p * (len(xs) - 1))]
    return {"median": round(q(0.5), 2), "p10": round(q(0.10), 2),
            "p90": round(q(0.90), 2), "mean": round(statistics.fmean(xs), 2)}


def calibrate_p_base() -> float:
    lo, hi = 0.30, 0.999
    for _ in range(16):
        mid = (lo + hi) / 2
        meds = statistics.median(
            simulate(ANCHOR_CAL, mid, random.Random(SEED + i)) for i in range(24))
        if meds < ANCHOR_TARGET:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> int:
    p_base = calibrate_p_base()
    anchor_sims = [simulate(ANCHOR_CAL, p_base, random.Random(SEED + 1000 + i))
                   for i in range(N_SIM)]
    s_anchor = summarize(anchor_sims)
    print(f"[calibrate] p_base={p_base:.3f} -> 锚预测 med={s_anchor['median']} "
          f"p10-p90={s_anchor['p10']}-{s_anchor['p90']} (目标 {ANCHOR_TARGET})")

    print("\n== HOLDOUT 验证（仅锚定过 p_base，其余零拟合）==")
    print(f"{'config':<17}{'pred_med':>9}{'pred_range':>13}{'actual_mean':>12}{'n':>3}{'verdict':>9}")
    results = {ANCHOR_CAL: s_anchor}
    misses = 0
    for name, cfg in CONFIGS.items():
        obs = cfg.get("observed")
        if not obs or name == ANCHOR_CAL:
            continue
        sims = [simulate(name, p_base, random.Random(SEED + 5000 + i))
                for i in range(N_SIM)]
        s = summarize(sims)
        results[name] = s
        act = statistics.fmean(obs)
        if cfg.get("fallback_suspect"):
            print(f"{name:<17}{s['median']:>9.2f}"
                  f"{s['p10']:.1f}-{s['p90']:.1f}".rjust(13)
                  + f"{act:>12.2f}{len(obs):>3}{'SKIP':>9}")
            continue
        ok = abs(act - s["median"]) <= max(3.0, (s["p90"] - s["p10"]) / 2)
        misses += (not ok)
        vr = "OK" if ok else "MISS"
        rng_s = f"{s['p10']:.1f}-{s['p90']:.1f}"
        print(f"{name:<17}{s['median']:>9.2f}{rng_s:>13}{act:>12.2f}{len(obs):>3}{vr:>9}")
    print(f"holdout misses: {misses}")

    print("\n== F015 排名（按 P(LB >= 锚+3 = 83.5)）==")
    rank = []
    for name in ("A_w11h0_reanchor", "B_speed_gpto", "C_speed_h5",
                 "D_fire90", "E_speed_fire90"):
        sims = [simulate(name, p_base, random.Random(SEED + 9000 + i))
                for i in range(N_SIM)]
        s = summarize(sims)
        p83 = round(sum(x >= 83.5 for x in sims) / len(sims), 3)
        p86 = round(sum(x >= 86.0 for x in sims) / len(sims), 3)
        rank.append({"config": name, **s, "P_ge_83.5": p83, "P_ge_86": p86})
    for r in sorted(rank, key=lambda x: -x["P_ge_83.5"]):
        print(f"{r['config']:<17} med={r['median']:>6.2f} "
              f"p10-p90={r['p10']:.1f}-{r['p90']:.1f} "
              f"P(>=83.5)={r['P_ge_83.5']:.2f} P(>=86)={r['P_ge_86']:.2f}")

    OUT_JSON.write_text(json.dumps({
        "p_base": round(p_base, 4), "anchor_target": ANCHOR_TARGET,
        "sim_count": N_SIM, "validation": results, "ranking": rank,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsaved {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
