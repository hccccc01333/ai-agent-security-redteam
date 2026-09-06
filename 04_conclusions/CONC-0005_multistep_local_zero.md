---
conclusion_id: CONC-0005
framework_id: F002
plan_id: P001
component_set: [C006, C007]
date: 2026-08-06
status: superseded（M1 公榜判据未定）
---

## 结论（局部定死）

- 时间：08-02 ~ 08-06
- 架构 / 思路：F002 多步链
- 方案：P001（M1）
- 组件组合：C006 链模板 + C007 本地门禁
- 数据 / 阶段：SDK 审计 + deterministic 代理
- 指标与证据：deterministic 代理 0 成交（EXP-011/012），但 SDK 合成 trace 证明 EXFIL 必触发、cell 与直发不同、guardrail 对 fs.write 内容 ALLOW

## 失败分类

角色错误（用 deterministic 代理当裁判判定多步链方向）；本地 0 成交 ≠ 公榜无效

## 重开条件

公榜信息实验（M1）判据：任一模型链式成交 ≥10% → 本结论（保守）不适用，方向成立；<10% → 冻结 F002。

## 最可能推翻本结论的证据

M1 公榜两模型链式成交均 ≥10%。
