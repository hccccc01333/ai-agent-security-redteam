---
component_id: C006
name: 多步 write→read→post 链
category: 表示
requirements: 单消息三步指令 + 显式工具名；文件/URL 随 index 变化
provenance: M1 Draft（2026-08-03，方向 A）
---

## 功能

制造与直发正交的链式 trace 新 cell 族。

## 输入 / 输出

输入：三步指令消息；输出：write→read→post trace。

## 适用思路

F002、F004。

## 已知效果（按思路×方案记录）

| 时间 | 思路 | 方案 | 角色 | 结果 |
|------|------|------|------|------|
| 08-03 | F002 | M1 v1（300/0.85） | Draft | v77 格式错误（环境窗口） |
| 08-04 | F002 | M1 v2（100/0.70） | Draft | local_pass；待重打 |

## 使用条件 / 失败模式

deterministic 代理不服从（EXP-011/012）；3 跳回放成本高 → 保守定容。
