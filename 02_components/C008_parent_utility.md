---
component_id: C008
name: 父效用三因子选择
category: 门控
requirements: score 1.0 / delta 0.4 / novelty 0.25 − 门禁惩罚 2.0；min-max + softmax
provenance: Frontis-MA1 Eq.4 源码默认权重（scripts/parent_utility.py）
---

## 功能

数值化选择下一父节点（质量/进步/新颖度），替代纯贪心最高分。

## 输入 / 输出

输入：注册表；输出：父效用排名。

## 适用思路

全部（调度层）。

## 已知效果（按思路×方案记录）

| 时间 | 思路 | 方案 | 角色 | 结果 |
|------|------|------|------|------|
| 08-02 | 调度 | parent_utility 首跑 | 工具 | F4 效用最高/Q5 第二（正确反映进步权重） |

## 使用条件 / 失败模式

公榜稀疏时 score 分量弱；最终提交仍人工口令，不自动采样。
