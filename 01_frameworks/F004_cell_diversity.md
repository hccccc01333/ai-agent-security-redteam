---
framework_id: F004
name: cell 多样性（正交 trace 签名）
status: 活跃（支撑/替代）
created: 2026-08-06
source: CONC-0005（candidate diversity > capacity）+ M1/x7 设计
---

## 问题定义（坐标系）

- 输入表示：多种 trace 形态（直发/链式/混合 bank/多模板）
- 输出表示：unique cell 集合（cell_signature(tool_events)）
- 解码方式：2 分/新 cell；多样性 = 独立于容量的分数来源

## 核心假设

直发族 cell 会饱和；新 trace 形态（写→读→发、bank 混合、不同 host/文件）带来新 cell。

## 典型组件组合

C005 bank 播种 + C006 多步链 + C004 模板族

## 已知强项 / 已知弱点

强：M1 链 cell 实测与直发不同；x7 bank 集中 others=0 但选型漂移仍在。
弱：R4（强制 inj_close）71.6 提示「集中」反向；混合族回放成本高。

## 反例证据（最能推翻本思路的证据）

正交 cell 增加但公榜不涨（cell 权重被护栏/模型差异淹没）。

## 换框触发器

单族 cell 饱和（每轮 ≈244 且 plateau）。

## 关联方案

F004/P001 多样性候选（x7、E 参考栈）。
