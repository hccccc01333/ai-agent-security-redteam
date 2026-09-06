# 每日提交流水线预案（防空窗）

> 起因：8/11 窗口 0 提交（浪费 5 枪）。规则：**每日 5 枪 = 4 预排 + 1 应急**，
> 只有 kernel ERROR 才停下修复，分数不回榜不阻塞后续枪。

## 当前主线（2026-08-12 起）

- 公榜可测主线：W 系自适应 EXFIL（W2→W3→W4→W5 阶梯，全部 PENDING）
- 私榜 hedge：fixture 引导 4%（W2-W5 内置，不可测、成本可控）
- 待 W 系回榜后收敛：选最高分代际，继续“旋钮/变异池/状态空间”微调

## 默认 4 枪模板（按优先级）

1. 当前最优 W 系 + 下一旋钮（变异池扩容 / 先验加权 / forge 链）
2. CONFUSED 保底复检（S2 结构，若 W 系全挂）
3. 公榜 W1 锚保排名（若当日无其他候选）
4. 新轴探针（fixture 引导 / UNTRUSTED / 模型分拆）

## 应急位（第 5 枪）使用条件

- kernel ERROR → 修复补交
- 当日某枪 early ERROR 且修复后仍可打
- 用户明确口令的决胜枪

## 执行纪律

- 门禁：local_sim（GO/分数）+ evaluate_candidate（mock 按族豁免）+ validate
- 每次提交后立即写 manifest + experiments + wall_survival
- 回榜后 30 分钟内对账并更新 CONC 台账
