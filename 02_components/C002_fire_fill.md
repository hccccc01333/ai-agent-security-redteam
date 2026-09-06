---
component_id: C002
name: 成交率填充器
category: 解码
requirements: 只 append fired 候选；fill_unit=中位成交延迟
provenance: v26 replay-safe 骨架
---

## 功能

用选中模板在回放预算帽内填满成交候选。

## 输入 / 输出

输入：selected_template、replay_cost_cap；输出：返回候选集。

## 适用思路

F001、F003。

## 已知效果（按思路×方案记录）

| 时间 | 思路 | 方案 | 角色 | 结果 |
|------|------|------|------|------|
| 07-26 | F001 | Q5 | 基础组件 | 87.795 |
| 08-03 | F003 | m1（Draft 改为无条件 append） | 角色变更 | 待公榜（v77 曾格式错误） |

## 使用条件 / 失败模式

- 本地 deterministic 成交不可观测时，fired-only 会返回空集 → Draft 模式改无条件 append（成本自校准）。
- 高方差模板导致回放超限 → REPLAY_SAFE 下调。
