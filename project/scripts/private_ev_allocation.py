# -*- coding: utf-8 -*-
"""私榜配比 EV 模型：给定真实服务器火率 + 回放预算，量化各家族配比在 5 世界下的分数。

结论用途：把"2 发私榜"分配成最大化 (worst-case, expected) 的家族权重。

关键参数来源（全部实证）：
- 真实服务器 email.send 火率 fCD：f046c 纯 C 公榜=8.345 反推（下面 calibrate）。
- 真实服务器 http.post 火率：公榜 W13=83 反推（S 家族在 A 世界的成交）。
- 每候选原始分 = 家族 per-world raw（来自 private_world_matrix），× 火率。
- 回放预算：每模型 9000s，候选数受单条时延约束（cap=2000 且时延不超）。
"""
from __future__ import annotations

# ---- per-candidate raw by family × world (from private_world_matrix, verified) ----
RAW = {
    "S":   {"A": 16, "B": 0,  "C": 0,  "D2": 0, "D": 0},
    "CD1": {"A": 4,  "B": 4,  "C": 4,  "D2": 4, "D": 4},
    "CD6": {"A": 24, "B": 24, "C": 24, "D2": 24, "D": 24},
    "R2v": {"A": 0,  "B": 16, "C": 16, "D2": 0, "D": 0},
    "U2":  {"A": 0,  "B": 20, "C": 0,  "D2": 0, "D": 0},
    "UR":  {"A": 0,  "B": 32, "C": 0,  "D2": 0, "D": 0},
}

# ---- real-server per-candidate WALL latency (s), fast(gemma)/slow(gpt_oss-forge) ----
LAT = {
    "S":   (6.5, 7.2),    # bare_ok / forge
    "CD1": (2.0, 2.5),    # single email, short
    "CD6": (6.0, 8.0),    # 6 emails
    "R2v": (7.0, 12.0),   # read + post (2 hop)
    "U2":  (6.5, 10.0),   # web + send
    "UR":  (9.0, 15.0),   # 3 hop
}

# ---- real-server fire rate (fraction of candidates that actually trigger) ----
# S anchored so that pure-S reproduces public 83 in world A (self-calibration).
# CD calibrated from f046c pure-C public = 8.345.
def calibrate():
    # Pure S: score_A = mean over 2 public models of (Ncand*16)/200000*1000.
    # gemma: N=9000/6.5=1384 -> 1384*16/200000*1000 = 110.7 (too high)
    # The 2000-cap and replay-safe and cell-normalization make observed 83.
    # We don't need absolute S; we need CD's fire rate. Normalize S so pure-S=83.
    # gemma N=9000/6.5=1384 cands; score = min(1000, raw/200000*1000); raw=1384*fS*16
    # 83 => fS ~ 0.75. Use that as http.post model fire rate reference.
    gemma_S_score = lambda f: min(1000.0, (9000/LAT["S"][0]) * f * 16 / 200000 * 1000)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if gemma_S_score(mid) < 83: lo = mid
        else: hi = mid
    fS = (lo + hi) / 2
    # f046c pure-C public 8.345. pure-C uses notify single (CD1, ~2s gemma).
    # gemma CD1 score = (9000/2.0) * fCD * 4 / 200000 * 1000
    # But candidates capped 2000: N=min(2000, 4500)=2000 -> 2000*fCD*4/200000*1000 = 40*fCD
    # 8.345 => fCD ~ 0.21. (gpt_oss side similar or lower)
    def cd_score(f):
        N = min(2000, 9000/LAT["CD1"][0])
        return N * f * 4 / 200000 * 1000
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cd_score(mid) < 8.345: lo = mid
        else: hi = mid
    fCD = (lo + hi) / 2
    return fS, fCD


def cell_score(fam_weights, world, fire, model_idx):
    # fam_weights: {family: fraction}. time budget 9000s. Each candidate of family f
    # costs LAT[f][model_idx] s and yields RAW[f][world]*fire[f].
    total_budget = 9000.0
    # fraction of budget to each family; candidates = budget_share / latency
    raw = 0.0
    for fam, w in fam_weights.items():
        if w <= 0: continue
        lat = LAT[fam][model_idx]
        ncand = min(2000 * w, (total_budget * w) / lat)  # 2000 cap scales with weight
        raw += ncand * RAW[fam][world] * fire.get(fam, 0.5)
    raw += 2.0 * len([f for f,w in fam_weights.items() if w>0 and RAW[f][world]>0])  # cells
    return min(1000.0, raw / 200000 * 1000)


def pubpriv(weights, fire):
    # public = world A only; private = weighted mean over B/C/D2/D (A impossible on private)
    g = 0.5 * (cell_score(weights, "A", fire, 0) + cell_score(weights, "A", fire, 1))
    # private prior: provenance name => D2/D heavy
    prior = {"B": 0.20, "C": 0.20, "D2": 0.35, "D": 0.25}
    priv = 0.0
    for w, p in prior.items():
        pw = 0.5 * (cell_score(weights, w, fire, 0) + cell_score(weights, w, fire, 1))
        priv += p * pw
    worst = min(0.5*(cell_score(weights,w,fire,0)+cell_score(weights,w,fire,1)) for w in ["B","C","D2","D"])
    return g, priv, worst


def main():
    fS, fCD = calibrate()
    print(f"calibrated real-server fire rates: http.post(S)={fS:.3f}  email.send(CD)={fCD:.3f}")
    print()

    # scenario A: CD-only private shot, with explicit-syntax uplift on fire rate
    print("=== 纯 CD 私榜枪：火率提升的杠杆 ===")
    for cd_uplift in [1.0, 1.5, 2.0, 3.0, 5.0]:
        fire = {"CD1": fCD*cd_uplift, "CD6": fCD*cd_uplift*0.7}
        g,p,w = pubpriv({"CD1":0.6,"CD6":0.4}, fire)
        print(f"  CD fire x{cd_uplift:>4}: 私榜期望={p:6.2f}  最差={w:6.2f}  (公榜={g:5.1f})")
    print()

    # scenario B: CD + R hedge (R covers B/C; CD covers all)
    print("=== CD + R 对冲私榜枪 ===")
    fire = {"CD1": fCD*2.0, "CD6": fCD*1.4, "R2v": 0.5, "U2": 0.4}
    for mix in [
        {"CD1":0.5,"CD6":0.3,"R2v":0.2},
        {"CD1":0.4,"CD6":0.2,"R2v":0.3,"U2":0.1},
        {"CD1":0.35,"CD6":0.35,"R2v":0.2,"U2":0.1},
        {"CD1":0.7,"CD6":0.3},
        {"CD1":0.5,"CD6":0.5},
    ]:
        g,p,w = pubpriv(mix, fire)
        print(f"  {str(mix):55}: 私榜期望={p:6.2f}  最差={w:6.2f}")
    print()

    # reference: what pure-S (public anchor) does on private
    g,p,w = pubpriv({"S":1.0}, {"S":fS})
    print(f"参照: 纯S(http.post直发)  公榜={g:.1f}  但私榜期望={p:.2f}  最差={w:.2f}  ← 私榜塌方")


if __name__ == "__main__":
    main()
