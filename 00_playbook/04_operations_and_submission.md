# 提交与运维（JED）

- 提交管线：`submit_one.ps1`（ast→validate→build→push→submit→早失效观察）；出分登记：`register_scores.py`（raw API 50 行）或 OS 监控任务。
- 纪律：用户口令才提交；一枪一版本；ERROR 即停；**单发验证再续发**（EXP-016）；当日额度 5 枪。
- 监控：OS 计划任务 `JED_W1_Monitor` 每 2h 同步；判线脚本 `judge_round.py`。
- 墙生存：提交前 `reports/wall_survival.md` 全量模拟（回放预算 <75% 时限）。
