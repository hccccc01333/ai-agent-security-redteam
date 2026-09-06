---
component_id: C009
name: 经验/禁令注册表
category: 数据
requirements: experience.jsonl（pattern/failure/evidence/ban/reconsider）+ registry.py check
provenance: 2026-07-23 起；EXP-001~016
---

## 功能

把失败转成结构化经验，提案前自动检索（≥2 token 重叠 → BAN）。

## 输入 / 输出

输入：变更描述；输出：BAN/RECONSIDER/NO_BAN。

## 适用思路

全部（调度层）。

## 已知效果（按思路×方案记录）

| 时间 | 思路 | 方案 | 角色 | 结果 |
|------|------|------|------|------|
| 08-02 | 调度 | EXP-013 硬阻断 MIN_FIRE>0.6 | 门禁 | 拦下 x5 提前开枪 |
| 08-04 | 调度 | EXP-016 连发禁令 | 门禁 | 单发验证纪律生效 |

## 使用条件 / 失败模式

ban 文案 token 需覆盖变体写法（EXP-013 曾漏匹配 MIN_FIRE=0.8，已修）。
