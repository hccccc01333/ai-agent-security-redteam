# 新路线实验 v1.0（2026-08-08）

依据官方 [733058](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/discussion/733058) 更新（清榜、Gemma 解析修复、回放超时保留部分分），本目录只做本地可验证的结构性收益，不消耗公榜枪位。

## 产出文件

| 文件 | 路线 | 结论（一句话） |
|------|------|------|
| `multi_post_local_probe.json` | A | K 个 ok post → K×16+2 raw；计分契约支持 multi-post，模型能否产出待公榜探针 |
| `replay_overshoot_curve.csv` + `replay_overshoot_meta.json` | B | 新规则下 1.05~1.10× 容量是收益拐点，旧 REPLAY_SAFE 偏保守 |
| `dual_predicate_local_eval.csv` + `dual_predicate_gate.json` | C | dual=22 raw，P_dual>0.736 才赢单谓词（P_single=0.9）；G2 即死 |
| `private_guardrail_calibration.csv` + `private_calibration_todo.json` | E | 本地无私榜分，需粘贴 5 个 ref 的 kernel Output |
| `new_routes_decision_v1.json` | 决策 | A=GO（模型轴待验）、B=GO、C=HOLD、D=HOLD、E=BLOCKED |

## 关键口径（源码级）

- 计分 cell = `cell_signature(tool_events)`（gateway 同款），不含用户消息文本。
- sandbox：guardrail DENY/CONFIRM/工具异常中断链；工具 ok=False 不中断。
- 回放预算 9000s/模型/护栏；超时保留已累计分（新规则）。

## 下一步

1. 用户粘贴 E 所需的 5 个 kernel Output（含 `[GATEWAY] ... = ...` 四行分）；
2. 用真实每候选耗时重跑 B（`python scripts/replay_overshoot_curve.py`）；
3. dual 模板进 W1 探针池（本地 mock 三盐 + replay_judge），成交率数据决定 C 是否转主线；
4. 以上做完再决定 D（F007 公榜探针）与 A 的多 post 真模型探针。

## 已批准顺序（2026-08-08）

E 日志补齐 → A 第一枪 → C 第二优先级。A1 探针变体已就绪并通过本地门禁：
`project/variants/w1_multi_post_probe.py`（W1 + multi_plain/multi_bare，选择器不变，日志带 v=/pf=）。

## NR-GATE v1（新路线门禁，2026-08-08）

执行：`python scripts/new_routes_gate.py`（在 project/ 下），结果写入 `new_routes_gate_v1.json`。

| 项 | 检查 | A1 当前 |
|------|------|------|
| G1 | A 计分契约探针（k2=34 / k5=82） | PASS |
| G2 | B overshoot 曲线产物存在 | PASS |
| G3 | C dual 评估 + EV 门槛（0.736） | PASS |
| G4 | E 私榜校准已回填真实行 | WARN（等日志） |
| G5 | A1 变体 registry local_pass（ast/smoke/mock 三盐） | PASS |
| G6 | 统一 G3 门禁（gate_submission.py，019fc04f 对话） | PASS（六项全绿） |
| G7 | 用户明确说“提交” | 待人工 |

总状态：READY_WITH_WARN（E 回填后 → READY；G7 由用户口头触发）。

## RS-GATE v1（返回分数门禁，2026-08-08）

执行：`python scripts/returned_score_gate.py --ref <submission_ref> --log <output.txt>`，或直接把 Output 文本 pipe 进 stdin。结果写入 `returned_score_gate_<ref>.json`。

| 项 | 判定 |
|------|------|
| G1 | 无 fatal 标记（Format Error / TimedOut / Kaggle Error） |
| G2 | 公榜分 ≥ 84.93 可接受；≥ 87.93 视为 promoted |
| G3 | 至少解析到 2 个私榜行分（gpt_oss_private / gemma_private）→ 回填 E |
| G4 | A1 判定：multi_* 模板 max pf ≥ 2 → GO_A2（multi-post 成立）；否则 NO_MULTI |

任何 FAIL → 按提交纪律停止，先修再打下一枪；只有 PASS 才允许进入下一轮。

## 双轨制与优先级（2026-08-08，用户修正版）

项目正式拆成两条线：

- **Track A（Aggressive）**：冲高分。指标 = raw/replay-sec、model transaction rate、runtime survival、ceiling。候选 = A / B / C / W1 family。
- **Track H（Hedge）**：私榜防守。指标 = guardrail survival、transaction floor、failure-mode independence、runtime reliability。候选 = CONFUSED 及其它低风险族。

最终两份提交默认 = 一个 aggressive + 一个 hedge（除非两条 aggressive 失败模式明显不同）。

优先级：**P0 W1 clean control → P1 等 A1/S1 → P2 C 类高 ceiling → P3 B 类高 ceiling → P4 CONFUSED hedge 去留**。

新增门禁（已实现）：

- G7-DV Decision Value Gate：`python scripts/decision_value_gate.py`（不是“至少两个问题”，而是“结果是否会改变后续决策”；全结果同决策 = NO-GO）。
- Ceiling / Hedge Gate：`python scripts/ceiling_hedge_gate.py`（aggressive 要求 ceiling≥90；hedge 要求最坏/次坏护栏下 floor 明显优于当前 hedge）。
- 配对选择器：`python scripts/pair_selector.py --matrix reports/new_routes_20260808/route_matrix.json`（U = Σ p_g·max，U_robust = 0.6·mean + 0.4·CVaR25%）。

## 提交账（2026-08-08 当日）

A1=55341285、S1=55340535、W1 clean=55342360 + 55342547（双对照）→ **当日已用 4/5，第 4/5 枪不再急打**；等三角结果回来再决定，宁可留空。E 口径修正：真实私榜行分赛前不可观测，只以 public/runtime/status/可见行为 更新 P(private regime)。

## 预注册判定与结果流水线（2026-08-08，结果回来前锁死）

- 判定表：`project/registry/pre_registered_decisions.json`（冻结；结果回来前不得修改）。
- 流水线：`python scripts/result_analysis_pipeline.py --results <triangle_json>`，固定 11 步：
  status → runtime → error/partial → W1 双样本(mean/range/mid) → H 归一 → 等价带 → RS-GATE → route status → pair selector → next-shot → W1 三分支。
- 等价带：`noise_band = max(practical_min_effect=3.0, W1_range)`；`|Δ| ≤ band` → **NO CLEAR EFFECT**（不写“略好/略差”）。
- W1×2 三分支：接近 → mean 当 control；差异大 → 区间基准、不点对点、必要时补第 3 control；任一 ERROR → W1 非 deterministic control，reliability 升权。
- 冻结令：**结果回来前不改 pair_selector 权重**；route_matrix 的 G-tier 只放 scenario score，reliability（completion/error/timeout）待真实结果回填，Observed 与 Derived 分层禁止重复计权。
