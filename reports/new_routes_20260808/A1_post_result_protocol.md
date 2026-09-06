# A1 收尾协议（提交后执行，2026-08-08）

提交：ref 55341285 / kernel v91 / 状态 PENDING（2026-08-08 04:52 UTC 提交）。
冻结：A1 代码不再改动；W1 不删、不覆盖、不重写（control）。
状态口径（registry/route_status.json）：W1_OLD_87.930=HISTORICAL_ONLY；W1_NEW_ERROR_76.770=INVALID_CONTROL；
W1_NEW_CLEAN=CONTROL_PENDING（refs 55342360 + 55342547，双对照估运行方差）；A1=EXPERIMENT_PENDING；S1=HEDGE_CALIBRATION_PENDING。

## 1. 第一时间回填 E

拿到 kernel Output 后跑：`python scripts/returned_score_gate.py --ref 55341285 --log <output.txt>`

回填记录字段：

```text
submission_id: 55341285
submit_time:   2026-08-08 04:52 UTC
public_score:
runtime:
status:
error_message:
model/runtime environment:
[GATEWAY] gpt_oss_public / gpt_oss_private / gemma_public / gemma_private:
multi v= / pf=:
```

## 2. W1 真实环境差分表

| 项 | W1 new control（refs 55342360 / 55342547） | A1（ref 55341285） | 判定 |
|------|------|------|------|
| Public score | 待填（两个样本） | 待填 | ΔA = A1 − W1_new |
| Runtime | 待填 | 待填 | 超时→ERROR 检查 |
| Successful candidates | 待填 | 待填（OK 数） | 成交率差分 |
| Tool-event pattern | 单 post/候选 | 待填（v=/pf=） | multi 是否成立 |
| Evaluator failures | 待填 | 待填 | 环境差异 |
| Sandbox exceptions | 待填 | 待填 | 代码/解析差异 |

归一化系数：H = W1_new / W1_old（87.930 仅作历史参照，不再直接横比）。

## 3. 结果判定（决策树，不过拟合）

**ΔA = A1 − W1_new（双 control 取均值/区间）**

| 情形 | 判定 | 动作 |
|------|------|------|
| A1 >> W1_new | multi-output 真实有效 | A family 升为 aggressive 主线，优化效率/稳定性，不改 wording |
| A1 ≈ W1_new | 结构复杂度无真实增益 | A family 暂停，不再微调 |
| A1 < W1_new | 多输出结构损伤成交轴 | A family kill |

**ΔS = S1 − N6B（CONFUSED 校准）**

- S1 明显改善 → CONFUSED 升级为 hedge candidate；
- S1 仍个位数 → CONFUSED 只保留理论研究价值，不再消耗提交额度。

**H = W1_new / W1_old（harness 归一化）**

- H 仅用于把历史实验换算到新坐标系；旧实验=historical reference，不做直接横比。

## 4. E 回填后的联动

- `private_guardrail_calibration.csv` 填入真实私榜行（G4 WARN → PASS）；
- 用真实每候选耗时重跑 `python scripts/replay_overshoot_curve.py` 定稿 B 容量；
- NR-GATE 复跑应为 7 PASS / 0 WARN / 0 FAIL（只剩 G7 用户触发）。

> E 口径修正（2026-08-08）：真实 private 行级评分在赛前基本不可观测；能拿到的只有
> public score / runtime / status / 可见 evaluator 行为 / 部分 replay 结果。因此
> 校准目标 = P(private regime)，不是直接估计 private score；配套 Scenario Matrix 见
> `route_matrix.json`，最终两枪按 `pair_selector.py` 的 U_robust 选。
