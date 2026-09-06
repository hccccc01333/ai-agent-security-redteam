---
conclusion_id: CONC-0024
framework_id: F010
plan_id: P7
component_set: [C001, C014]
date: 2026-08-10
status: active
---

## 结论（假设审计：私榜行为未验证，W1/EXFIL 升回主力，所有“关轴”降级为“未解决”）

- 时间：2026-08-10（用户质疑后重审，参照 ROGII 教训：高分方案常来自被冻结路径）
- 事实 vs 假设：
  | 项 | 状态 | 证据 |
  |----|------|------|
  | 公榜 W1 锚 82.9、CONFUSED S2 13.3 | 事实 | 线上分数 |
  | 私榜 = persistent_provenance / 内容 DLP / 无网络 | **假设** | 我们自写 private_proxy；SDK 只带 OptimalGuardrail；社区代理均为 guess |
  | W1 私榜必死（http.post SECRET_MARKER 被拒） | **假设** | 从未见过私榜分数 |
  | CONFUSED 是唯一私榜存活通道 | **假设** | 同上 |
  | multi-send 无效（S4 vs S6 不一致） | **未解决** | 两个样本互相矛盾，需同 N A/B |
  | 扩容饱和（2000≈1250） | 部分事实 | 噪声内持平，但机制未明 |
  | 家族混合必稀释（N6B 8模板 / S5 空分） | **未解决** | 只测过 2 种混合 |
- 推论：
  - W1/EXFIL（severity 5 → 权重 16）重新升为**主力线**：它是唯一可能在
    宽松型私榜下直接 80+ 的族；CONFUSED 保留为严格型私榜保险，不作主力；
  - F009 的 mutation/archive/selector 机器应该作用在 EXFIL 高收益模板上
    （此前用在 CONFUSED 低收益族 = “方法用错地方”的候选解释）；
  - 所有“closed/冻结”状态改为“parked（未解决）”，带重开条件；
- 失败分类：其他（框架困境：用自建假设代理替代未知真实护栏，导致错误关轴）
- 重开条件：① 任何能获得私榜信号的渠道（终榜、日志、官方回复）；
  ② EXFIL mutation 枪（公榜可测，若私榜宽松则直接命中）；
  ③ multi-send 同 N A/B；④ 2-3 族精选混合（不再 8 模板乱混）。
