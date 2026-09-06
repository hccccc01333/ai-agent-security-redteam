---
component_id: C010
name: 提交管线
category: 运维
requirements: submit_one.ps1 + validate_submission + build_submit_notebook + register_scores
provenance: 2026-07-23 起；v71~v81
---

## 功能

一枪一版本：ast→validate→build→push→submit→早失效观察→出分登记。

## 输入 / 输出

输入：变体 + 口令；输出：kernel vN / ref / registry 更新。

## 适用思路

全部（执行层）。

## 已知效果（按思路×方案记录）

| 时间 | 思路 | 方案 | 角色 | 结果 |
|------|------|------|------|------|
| 08-02 | 运维 | v71-v75 | 执行 | 5/5 正常出分 |
| 08-03 | 运维 | v77-v80 连发 | 执行 | 4/4 格式错误（EXP-016） |
| 08-04 | 运维 | v81 单发 | 执行 | 待出分 |

## 使用条件 / 失败模式

禁止连发；单发验证后再续发；ERROR 修复须当日额度内。
