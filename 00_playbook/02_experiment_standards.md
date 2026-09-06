# JED 实验规范（硬标准，2026-08-06 按资产包锁定）

1. **一枪一张可比表**：时间、单旋钮改动、父锚点、公榜分、判定（promoted/rejected/error）。口径锁定 W1=87.930 起。
2. **指标锁死**：主指标=公榜；辅助=成交 finding / unique cell；不得把 mock 通过当公榜证据。
3. **日志即事实**：每枪在 `03_experiments/<F>/<P>/component_log.csv` 记一行；没有日志的实验不存在。
4. **失败必须分类**：死胡同 / 角色错误 / 时机错误 / 成本放弃 / 其他；只有死胡同可关闭，且仍写重开条件。
5. **结论必须可回溯**：每条结论指回实验日志与组件。
6. **null 对照强制**：旋钮候选过 mock 3 盐；历史锚点回归；信息实验必须有预设判线（如 M1 ≥10% 成交）。
7. **防自欺审计**：本地门禁不预测模型行为轴（EXP-013/015 校准结论）；公榜只当固定偏移。
8. **确定性**：攻击 seed 固定 123；变体哈希落库（evaluate_candidate）。
9. **审计节奏**：每 3~5 枪框架审计；阶段结束写复盘（05_retrospectives）。

## 日志格式

```text
timestamp,framework_id,plan_id,component_id,action,experiment_id,role,result_summary,note
```

`action`: plan / use / abandon / reopen。
