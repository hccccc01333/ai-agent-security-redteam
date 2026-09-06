# P002 N3 tools-only 多样性归档（F004）

- 日期：2026-08-06；父方案：W1（87.93 锚点）/ P001（E 系冻结、x7 ERROR）。
- 假设：**返回集按 tools-only 签名族归档并族间轮转，比“只填选中族”获得更高 unique cell 覆盖，且成交密度不显著下降**（Go-Explore Red Team：简单签名>复杂；Rainbow Teaming：行为特征空间归档）。
- 变更（一次一桶）：W1 的“探针选单族 + 只填选中族” → “探针门禁族集合 + 族间轮转填充”；归档键=成功工具事件去重序列（本地退化为模板族近似）。
- 预期机制：真模型上不同模板族（plain/bare/inj_close/inj_commentary）行为签名不同 → 多族候选 × host 轮换 = 更多 unique cell；预算不变（每候选仍 1 消息/8 hops）。
- 本地门禁：
  - G1：AST/no_op/smoke allow+optimal（沿用 evaluate_candidate）。
  - G2：mock 3 盐通过（族分布 ≥2 族）；replay judge 不超时；wall_survival 300s 不崩。
  - G3：公榜判定——总分 ≥ W1(87.93) → promoted 继续同轴；回落 → 回 W1 单族填充。
- 风险：多族混合稀释最高成交族 → F 下降；本地无成交（deterministic 0 fire），族区分度只能公榜验证；REPLAY_SAFE 保持 0.996，用实测 elapsed 累计保预算安全。
- 冻结范围：SDK/评分器/护栏/data 不改；只改 `variants/n3_tools_only_archive.py`。
