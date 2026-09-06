---
conclusion_id: CONC-0027
framework_id: F010
plan_id: P10
component_set: [C001, C014, C015]
date: 2026-08-12
status: active
---

## 结论（W2 已提交；W3 状态空间已建；最小先验学习器已上线；x5 无增益；S5 静默失败坐实）

- 时间：2026-08-12 19:30 +08
- 指标与证据：
  - x5（W1 MIN_FIRE 0.8）= **COMPLETE 82.845** ≈ W1 锚 82.89/81.495 →
    **MIN_FIRE 0.8 无增益**，公榜旋钮暂不继续；
  - S5（四族 balanced）2 天仍 COMPLETE 空分 → **静默失败坐实**，配方冻结；
  - **W2 adaptive EXFIL 已提交**（ref 55457208，v101）：W1 自适应核心 +
    7 模板运行时路由 + REPLAY_SAFE 0.90 + 4% fixture hedge；
  - **W3 state EXFIL 已建**（w3_state_exfil.py）：W2 + env.snapshot()/restore()
    同状态分支探测，本地 mock 已支持 snapshot/restore，门禁 36.00/GO、mock 3/3；
  - **最小先验学习器**（learn_priors.py → template_priors.json）：
    direct_notify 1.80 raw/交互（n=3）、direct_notify_multisend 2.23（n=2）、
    notify_direct 1.59（n=1）——先验表用于后续模板库排序；
  - 8/11 窗口 0 提交（5 枪浪费）——流水线纪律需恢复。
- 推论：
  - 公榜主线 = W2/W3 自适应 EXFIL（可测）；私榜世界 B = fixture hedge（不可测，
    4% 成本可控）；
  - 三个缺口进度：状态空间 ✅（W3 已建待打）、进化/变异 ⏳（Mutator 待接入
    运行时循环）、混合学习 ✅ 最小版（先验表，bandit 待数据）；
  - 追加：W2（55457208）/W3（55457457）已提交；**W4 mutate 已建**
    （16 变异模板运行时探测，mock 门豁免按 N6/N6B 先例，local 36/GO）；
- 失败分类：其他（8/11 空窗 = 流程执行中断，非技术失败）
- 重开条件：① W2 回榜 → 判线 ≥82.89 推进 W3；② W3 回榜 → 状态空间是否有
  真增益；③ x5/S5 结论已定（无增益/冻结）。
