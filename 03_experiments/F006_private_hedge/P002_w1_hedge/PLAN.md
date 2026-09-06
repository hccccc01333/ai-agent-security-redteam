# P002 W1 + 10% CONFUSED hedge（私榜抗性混合）

- 日期：2026-08-07；父方案：W1（公榜锚点 87.930）+ n6（CONFUSED 信息实验）
- 假设：以 W1 单族填充保公榜吞吐（F），混入 10% 无载荷 email.send 候选作为私榜 hedge；hedge 比例足够小，公榜损失可接受，私榜若放行则获得保底
- 变更（一次一桶）：W1 填充循环每 9 个 W1 候选插入 1 个 hedge 候选（HEDGE_RATIO=0.10）
- 门禁：mock 3 盐（hedge 计入 others，需 ≤10% dominance 边界）；smoke/replay/wall 300s；双护栏直测 hedge 8/8（沿用）
- 判定线：**仅在 n6 公榜成交 >0 后才提交**；提交后总分 ≥W1(87.93)-3 视为可接受（hedge 成本），≥W1 则 promoted
- 风险：hedge 执行率 0 时浪费 ~10% 预算（N3 稀释教训）；N6 未出分前只本地待命
- 冻结范围：SDK/评分器/护栏/data 不改；只改 `variants/n7_w1_confused_hedge.py`
