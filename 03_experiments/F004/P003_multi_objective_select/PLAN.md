# P003 N5 多目标选择（F004）

- 日期：2026-08-06；父方案：N3（P002，已提交 ref 55297758）。
- 假设：**填充选择 = 成交成本分 × 新签名族奖励（族已返回越多奖励越低），比平均轮转更优**：前期补 cell 多样性，后期收敛到高成交族保 F（EvoJail diversity-aware fitness / BlackDAN 多目标 / Novelty Search）。
- 变更（一次一桶）：N3 的族间 round-robin → deterministic 加权轮转（Largest-Remainder：每步选“按权重欠分配最多”的族）。
  - weight_i = (fire_rate_i / cost_i 归一化) × (1 + NOVELTY_LAMBDA / (1 + returned_i))
  - NOVELTY_LAMBDA = 1.0（常量，本桶不调）。
- 本地门禁：
  - G1：AST/no_op/smoke allow+optimal（沿用 evaluate_candidate）。
  - G2：mock 3 盐族分布 ≥2、2000 候选、无异常（沿用 n3_archive_check，加 --variant）。
  - G3：公榜判定——与 N3 总分比较：≥N3 → promoted；<N3 且 <W1(87.93) → 回 W1 单族。
- 风险：novelty 奖励可能把预算分给低成交族 → F 下降；本地无成交，只能公榜判定。
- 冻结范围：SDK/评分器/护栏/data 不改；只改 `variants/n5_multi_objective.py`。
