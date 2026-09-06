# P001 N6 CONFUSED hedge（私榜抗性）

- 日期：2026-08-07；依据：CONC-0010（private_proxy 审计）、09_公私榜差异、官方原文（私榜=更严护栏）
- 假设：无载荷 email.send（用户句避开 send/email/upload 字面）在公榜 Optimal 与私榜 persistent_provenance 双护栏下都放行；真模型执行率需公榜验证
- 变体：variants/n6_confused_hedge.py（8 中文模板 / 500 候选 / 收件人轮换）
- 门禁：双护栏直测 8/8 ALLOW；smoke/wall 300s 通过；本地 hits=0（deterministic 不执行中文 email.send，属预期）
- 判定线：公榜 CONFUSED 成交 >0 → hedge 成立，考虑 W1+小比例混合；=0 → CONFUSED 不可行，私榜抗性需另寻
- 冻结范围：SDK/评分器/护栏/data 不改
