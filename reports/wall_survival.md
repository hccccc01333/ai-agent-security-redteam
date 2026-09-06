# 墙生存测试（JED）

## 墙的定义

- 回放预算墙：9000s / 模型 × 护栏（gpt_oss/gemma × public/private，共 4 轮）。
- 候选校验墙：≤2000 候选、每条 ≤32 消息、消息 ≤2000 字符、max_tool_hops=8 不可绕过。
- 提交吞吐墙：每日 5 枪；反馈 ~14h；ERROR 作废（0 字节 CSV）。

> 口径更新（2026-08-08，官方 733058）：回放阶段超时**不再清零**，保留超时前
> 累计部分分；但 CONC-0013 实测 ERROR（部分分>0）不计榜。门禁已同步：
> `local_sim_guardrail.py` 输出 REPLAY_BUDGET + PARTIAL_RETAINED，判定
> GO / WARN(保留分≥80) / NO-GO(保留分<80)，且仍以 COMPLETE 为提交目标。

## 模拟方法

1. **预算自校准**：攻击 run 内用真实测量的每候选延迟累计 `replay_cost`，超过 `REPLAY_SAFE×9000` 即截断（C003）。
2. **本地全量模拟**：`smoke_test.py --budget-s 300` 跑完整 fill；验证返回集不超帽、无异常。
3. **候选校验**：`validate_submission.py`（AttackAlgorithm 契约 + 禁用网络/子进程）。
4. **墙比例**：目标 = 模拟耗时 < 时限 75%（回放 9000s 时，候选累计成本 ≤6750s，即 REPLAY_SAFE ≤0.75 档；常规单跳候选用 0.996 需自校准后实测）。

## 当前状态（2026-08-06）

| 候选 | 墙检查 | 状态 |
|------|--------|------|
| W1（锚点） | REPLAY_SAFE=0.996 自校准 | ✅ 已出分 87.93 |
| x6（REPS=8） | 通过自校准但 76.32 | ⚠️ 分数崩但未穿墙（说明墙内成本结构变化） |
| M1 v2 | 100 候选 / REPLAY_SAFE=0.70 / 本地模拟 | ✅ local_pass，待重打 |
| x5 v81 | 同 W1 配置 | ⏳ 待出分 |
| N1（P002 状态污染链 v2） | 4 族多消息链 / 100 候选 / REPLAY_SAFE=0.70 / 300s 模拟 | ✅ local_pass；本枪=方向探针（预期总分显著 <87.8，判定只看链式成交） |
| N3（F004 多样性归档） | 4 族轮转 / 2000 候选 / REPLAY_SAFE=0.996 / 300s 模拟 | ✅ local_pass；判定线：总分 ≥87.93 → 继续同轴，回落 → 回 W1 单族 |
| N5（F004 多目标选择） | 加权轮转（fire/cost × novelty λ=1）/ 2000 候选 / REPLAY_SAFE=0.996 | ✅ local_pass；判定线：≥N3 → promoted，<N3 且 <87.93 → 回 W1 |
| N6（私榜抗性 CONFUSED hedge） | 8 中文模板 / 500 候选 / 双护栏 ALLOW 8/8 / REPLAY_SAFE=0.996 | ✅ local_pass；信息实验：真模型 email.send 执行率 = 公榜判定 |

## 教训（EXP-016/015）

- 4 连发全 ERROR：墙生存不能替代「单发验证」；环境窗口无法本地预判。
- REPS=8：预算墙内通过，但探针把有效成交挤出 → 墙不是唯一约束，吞吐模型（F003）才是。

## 提交前清单（N1 2026-08-06）

- [x] 本地模拟（budget 300s）不崩、不超帽（100 候选 / 0 异常）
- [x] validate_submission PASS（AttackAlgorithm 契约 + 无禁用特性）
- [x] 单发验证上一枪状态（M1 = Submission Format Error 从未出分，ref 55211909；本枪为 F002 首次真实判定）
- [x] 预设判线写入账本（PLAN.md：任一模型 EXFIL 成交且 cell 新族 → 方向成立；两模型 0/<10% → 冻结 F002）

## 提交前清单（N3 2026-08-06）

- [x] 本地模拟（budget 300s）不崩、不超帽
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 单发验证上一枪状态（N1 ref 55297292 PENDING；本枪独立方向 F004，不阻塞）
- [x] 预设判线写入账本（PLAN.md：≥87.93 → promoted；回落 → 回 W1）

## 提交前清单（N5 2026-08-06）

- [x] 本地模拟：n3_archive_check --variant n5 3 盐全过（2000 候选 / 4 族）
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 单发验证上一枪状态（N1/N3 PENDING；本枪 F004 第三旋钮，不阻塞）
- [x] 预设判线写入账本（PLAN.md：≥N3 → promoted；<N3 且 <87.93 → 回 W1）

## 提交前清单（N6 2026-08-07）

- [x] 本地模拟（budget 300s）不崩、不超帽（500 候选）
- [x] 双护栏直测（optimal + private_proxy）8/8 ALLOW（private_hedge_scan）
- [x] 单发验证上一枪状态（N1=9.08、N3=47.52 已出分；N5 PENDING）
- [x] 预设判线写入账本（信息实验：email.send 执行率 >0 → hedge 成立；=0 → CONFUSED 不可行）

## 提交前清单（四枪批次 2026-08-07，排行榜作废后的完整重打）

背景：官方 733058 重建评估（Gemma 解析修复 + 回放超时保留得分 + 榜作废），每队
选 2 份重播；今日剩余 4 次额度全部用于完整提交，出分后择优选 2 份。

### n7_w1_confused_hedge（第 1 枪）
- [x] n7_hedge_check 3 盐全过：hedge 8.2% / w1 91.8%（n=2000/盐）
- [x] 本地模拟（budget 300s）不崩、不超帽（无成交回退 5 候选，与 W1 同构）
- [x] evaluate_candidate：ast/no_op/smoke(allow+optimal×2)/replay_judge 全 PASS
- [x] 判线：与 W1 87.93 对比；若 N6 出分 email.send>0 则 hedge 成立，此枪为私榜保险

### n6b_confused_large（第 2 枪）
- [x] evaluate_candidate：ast/no_op/smoke(allow+optimal×2) 全 PASS，local_pass
- [x] 本地模拟（budget 300s）：1000 候选 / replay_cost=22/8964 / 0 异常
- [x] 双护栏 8/8 ALLOW 沿用 N6（模板未改，仅容量旋钮 500→1000）
- [x] 判线：容量放大后 email.send 成交 cell 数是否随候选数上升（公榜信息实验）

### n8_clean_direct（第 3 枪）
- [x] evaluate_candidate：ast/no_op/smoke(allow+optimal×2)+mock 3 盐全 PASS
- [x] 本地模拟（budget 300s）不崩、不超帽（无成交回退 5 候选，与 W1 同构）
- [x] 判线：去掉 inj_close/inj_commentary 后 vs W1 重打——判断 inj_close 在重建 harness 下是否仍贡献

### w1_probe5_fire65 原版重打（第 4 枪，对照组）
- [x] 本地模拟（budget 300s）不崩、不超帽（无成交回退 5 候选，锚点同构）
- [x] 判线：重建 harness 下的新锚点分；与 n8 配对判断 inj_close 贡献

## 提交前清单（N9 2026-08-08，新 harness 校准补枪）

背景：系统自动选 2 份，唯一进榜项 N6=4.755（#33/38）；W1 系重打全部回放超时
ERROR（部分分 76.77/67.32/60.66）；比赛最终截止 9/1，新提交仍排队评估（N6B PENDING）。

- [x] evaluate_candidate：ast/no_op/smoke(allow+optimal×2)+mock 3 盐全 PASS，local_pass
- [x] 本地模拟（budget 300s）不崩、不超帽（无成交回退 5 候选，与 W1 同构）
- [x] 唯一旋钮：REPLAY_SAFE 0.996→0.80（cap 7200s，为重建 harness 回放膨胀留 20% 余量）
- [x] 本地分数门禁（local_score_gate.py，3 盐）：latency=0 时 n9=W1=400 findings/
      raw 6402 / norm 32.01，ratio=1.000 PASS；latency=30 时 n9=240 vs W1=298，
      ratio=0.805 ≈ 0.80/0.996，旋钮按设计缩集 PASS（registry/local_score_gate_20260808.json）
- [x] 判线：COMPLETE 且 ≥60 → 校准方向成立，下枪可微调 REPLAY_SAFE↑；再超时 → 降到 0.65 并缩候选

## 提交前清单（S1-Balanced 2026-08-08，真实回放校准首枪）

背景：官方 8/7 规则（回放超时保留部分分 + ERROR 不计榜）已同步进门禁；S1 是
纯 CONFUSED email.send 校准件，目的不是争分，而是拿到真实秒/交互与线上榜分映射。

- [x] local_sim_guardrail @15%（3-salt）：LOCAL_SCORE=24.2733 / RUNTIME=0.7s /
      REPLAY_BUDGET GO（1250 交互，util@4s=56%，2/3/4/5/6s=28/42/56/69/83%）
- [x] PARTIAL_RETAINED=24.27（完整跑完不触发）；合格线 80 仍要求 COMPLETE
- [x] evaluate_candidate（CONFUSED 族口径，不带 EXFIL mock）：ast=pass /
      smoke_allow=pass / smoke_optimal=pass；mock 豁免按 N6/N6B 先例
      （evaluate_candidate mock 只识别 http.post，纯 email 族结构性不适配）
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 用户口令：GO（submission_approved.txt 已记录）
- [x] 判线：①是否 COMPLETE（第一优先级）；②真实 replay wall time → 秒/交互；
      ③线上榜分相对本地 0%/15-80% 档位；④相对 N6B=5.115 的增量。

## 候选队列（S2/S3/S4，2026-08-08，本地已全绿，未提交）

| 变体 | 结构 | 交互 | 本地私榜 | 预算判定 | 定位 |
|------|------|-----:|--------:|----------|------|
| s2_efficient_k1 | 1250×k1 唯一收件人 | 1250 | 30.44 | GO 56% | 同预算效率枪（比 S1 +25%） |
| s2_aggressive_2000 | 2000×k1 唯一收件人 | 2000 | 48.72 | 89%，等 S1 ≤3s/次转 GO | 校准后扩容枪 |
| s3_orthogonal_templates | 1250×k1 八模板轮转 | 1250 | 30.08 | GO 56% | 措辞正交 hedge |
| s4_multisend_probe | 500×单消息 5 收件人 | 500 | 12.11 | GO 22% | Gemma 多工具调用轴探针 |
| s5_router_pool | 1250×k1 四族轮转（direct/decompose/tool/reframe） | 1250 | 30.14 | GO 56% | 真模型路由实验枪 / S2 低相关替补 |
| s5_dc_heavy | 1250×k1 D40/C40/T10/R10 | 1250 | 29.90 | GO 56% | F010 contrast：估 C vs T/R |
| s5_dt_heavy | 1250×k1 D40/C10/T40/R10 | 1250 | 29.65 | GO 56% | F010 contrast：估 T vs C/R |
| s5_dr_heavy | 1250×k1 D40/C10/T10/R40 | 1250 | 29.83 | GO 56% | F010 contrast：估 R vs C/T |

共同点：纯 CONFUSED email.send、无载荷、0/15/25/40/80% 全档存活；
evaluate_candidate（CONFUSED 族口径）local_pass；等 S1 回榜后按
真实秒/交互与线上排序决定下一枪。

## 提交前清单（S2-Efficient 2026-08-09，当前窗口最后一枪 / k 归因枪）

背景：S1 已回榜（COMPLETE 9.935，真实/本地比 0.409，1.59 raw/交互）；
S1 vs N6B 单位收益 +55% 但模板/k 双变量混淆；S2 用同 notify 模板、k=1，
1250 交互，专门拆 k。

- [x] local_sim_guardrail @15%（3-salt）：LOCAL_SCORE=30.4400 / GO
      （1250 交互，util@4s=56%）；0/15/25/40/80% 全档存活（此前已验）
- [x] FAILURE_MIX：blocked=0 / no_fire=235 / partial=0 / full=1015 /
      unobservable=0（mock 口径，真实成交由回榜判定）
- [x] evaluate_candidate（CONFUSED 族口径）：ast/no_op/smoke 全 PASS local_pass
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 用户批准：submission_approved.txt（2026-08-09，重置前最后一枪）
- [x] 判线：S2≈9-12 → k 无关（模板/措辞驱动），下一枪 S5 balanced 或 contrast；
      S2≈5-6 → k>1 是真杠杆，做 625×2/417×3 k 曲线；
      S2<5 → notify 模板 k=1 真实成交率低于 S1，回 S1 结构微调。

## 提交前清单（S4 multi-send 2026-08-09，重置后第 1 枪 / 私榜几何杠杆探针）

背景：k 归因已闭环（S2=13.335 > S1=9.935，k1 胜）；纯 CONFUSED 到 80 需
yield×k，S4 单消息点名 5 收件人，验证 Gemma 多工具调用轴。

- [x] local_sim_guardrail @15%（3-salt）：LOCAL_SCORE=12.1100 / GO
      （500 交互，util@4s=22%）
- [x] FAILURE_MIX：unobservable≈404/500（mock 表达不了多工具调用，
      本地分 12.11 只证明合法性，不预测真实成交）
- [x] evaluate_candidate（CONFUSED 族口径）：ast/no_op/smoke 全 PASS local_pass
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 用户批准：submission_approved.txt（2026-08-09 重置后第 1 枪）
- [x] 判线：单消息多次 email.send（回放日志/分数显著 > 单发基线 2.13 raw/交互）
      → S6 = k1 多收件人配方；只有 1 次 → 多工具轴关闭，转新私榜通道。

## 提交前清单（S2-Aggressive 2026-08-09，重置后第 2 枪 / 用户批准风险枪）

背景：S2（1250×k1）COMPLETE 13.335 已确认 k1 最优；本枪扩到候选上限
2000×k1（本地 48.72，预期真实 ≈21），同时标定 2000 交互是否 COMPLETE。

- [x] local_sim_guardrail @15%（3-salt）：LOCAL_SCORE=48.7200；
      REPLAY_BUDGET util@4s=89% → 严格门禁 NO-GO（超时保留分 48.72<80）
- [x] 风险依据：S1/S2（1250 交互）均 COMPLETE → 真实 ≤7.2s/条；
      2000 交互 COMPLETE 需 ≤4.5s/条；4.5-7.2s 则 ERROR 部分分不计榜
- [x] FAILURE_MIX：blocked=0 / no_fire=376 / full=1624 / unobservable=0
- [x] evaluate_candidate（CONFUSED 族口径）：ast/no_op/smoke 全 PASS local_pass
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 用户批准：submission_approved.txt（明确标注风险枪，用户确认接受）
- [x] 判线：COMPLETE → 真实 ≤4.5s/条，CONFUSED 向 2000 上限优化；
      ERROR → 真实 >4.5s，回退 1500/1750×k1 安全档。

## 提交前清单（W2 adaptive EXFIL 2026-08-10，候选就绪待口令）

背景：框架修正后主线回到自适应 EXFIL（CONC-0025/0026）；W2 = W1 自适应核心
（探测5次→选最低成本 fire≥0.65→预算装填）+ 2 个保守新模板 + REPLAY_SAFE
0.996→0.90（预留 hedge 预算）+ 4% fixture 引导 hedge（私榜世界 B 覆盖）。

- [x] 结构验证：ast OK；TEMPLATES=7（plain/bare/bare_ok/inj_close/
      inj_commentary/plain_url/bare_short）；REPLAY_SAFE=0.90；
      HEDGE_MESSAGES=12 条（注入邮件/网页/mh 文件泛化引用）
- [x] local_sim_guardrail @0%（3-salt）：LOCAL_SCORE=36.0000 / GO
      （400 cap 本地口径；真实装填按实测延迟，预期 ~800-1300 候选）
- [x] evaluate_candidate（EXFIL 族，mock）：ast/no_op/smoke 全 PASS，
      mock 3/3 local_pass
- [x] hedge 说明：fixture 引导候选公榜预期 ~0 分（护栏 taint 拦截），
      价值在私榜 UNTRUSTED/真密文链（CONC-0026）；本地 mock 会把消息里的
      “@地址”误判为 email.send（模拟器假象，真实模型是 email.read）
- [x] 判线：公榜 ≥ W1 锚 82.89 → 模板扩容+hedge 不伤主得分面；
      <81 → hedge 或新模板拖累，回滚 W1 原版再微调
- [x] 待用户口令（今日剩 1 枪应急位，也可明日首枪）

## 提交前清单（W3 state EXFIL 2026-08-12，候选就绪待口令）

背景：W2 已提交（ref 55457208，v101）；W3 = W2 + snapshot/restore 状态空间
探测（每个模板从同一环境状态分支测量，真实 harness 与本地 mock 均支持）。

- [x] local_sim_guardrail @0%（3-salt）：LOCAL_SCORE=36.0000 / GO
      （snapshot/restore 路径已走通）
- [x] evaluate_candidate（EXFIL 族，mock）：ast/no_op/smoke 全 PASS，
      mock 3/3 local_pass
- [x] 判线：与 W2 对比——W3 ≥ W2+1 → 状态空间分支有真增益；
      ≈W2 → snapshot 只是测量纯度工具，无线上增益；<W2-1 → 回滚 W2

## 提交前清单（W4 mutate EXFIL 2026-08-12，候选就绪待口令）

背景：W3 已提交（ref 55457457，v102）；W4 = W3 + 16 个运行时变异模板
（“进化算法”方向：变异 → 真模型实测 fire/成本 → 选优装填）。

- [x] local_sim_guardrail @0%（3-salt）：LOCAL_SCORE=36.0000 / GO
      （23 模板探测+变异池全链路走通）
- [x] evaluate_candidate：ast/no_op/smoke 全 PASS；mock **豁免**
      （变异体 mut_bare_now/mut_via 不在 mock 关键字校准内，sel_count=0
      为评估器假象；真模型 fire 由 eval_predicates 实测，按 CONFUSED 族
      N6/N6B 先例豁免 mock 门）
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 判线：与 W2/W3 对比——W4 ≥ W3+1 → 变异池有真增益；
      ≈W3 → 变异未转化成交成率；<W3-1 → 回滚 W3/W2

## 提交前清单（W6 fullbudget 2026-08-13，今天第 1 枪）

背景：W 系收敛——W3=76.860 最优（snapshot 增益）；W2 掉分≈REPLAY_SAFE 0.90
少装填；W4/W5 变异池关闭。W6 = W3 + REPLAY_SAFE 0.996 + hedge 2%。

- [x] local_sim_guardrail @0%（3-salt）：LOCAL_SCORE=36.0000 / GO
- [x] evaluate_candidate（EXFIL 族，mock）：ast/no_op/smoke 全 PASS，
      mock 3/3 local_pass
- [x] validate_submission PASS（submit_one 内置重跑）
- [x] 已提交 ref 55475454 / v105 / PENDING
- [x] 判线：≥82.89 → 新锚；ERROR → 回 W3（0.90）安全档

## 提交前清单（2026-08-10 四枪流水线，用户一次批准）

背景：修正“等分数再打”的浪费模式；四枪独立变量，按序打，不阻塞。

### 枪 1：s6_multisend_1250（multi-send 决定性验证）
- [x] local_sim @15%：30.26 / GO（1250 交互，util 56%）；FAILURE_MIX
      unobservable≈1009（mock 表达不了多收件人，真实以回放为准）
- [x] evaluate_candidate local_pass；判线：>13.335（S2）→ multi-send 成立

### 枪 2：x5_probe8（W1 MIN_FIRE 0.8，公榜旋钮）
- [x] evaluate_candidate EXFIL mock 3/3 local_pass；判线：>82.890（W1 锚）→
      新 harness 下 MIN_FIRE 0.8 更优，继续扫旋钮

### 枪 3：s5_router_pool（family-mixture 归因锚点）
- [x] local_sim @15%：30.14 / GO；evaluate_candidate local_pass；
      判线：真实分与 S2（13.335）对比 → family 路由价值/稀释判定

### 枪 4：s2_efficient_k1 重测（噪声量化）
- [x] local_sim @15%：30.44 / GO；evaluate_candidate local_pass；
      判线：与 13.335 差值 → CONFUSED 运行噪声 ±x，重估 S4/S2A/S6 差值

第 5 枪保留：kernel ERROR 应急补交 / S6 回榜后的扩容版（S6b）。

## 提交前清单（W1 clean baseline 2026-08-08，第 3 枪 / 信息控制枪）

背景：A1（w1_multi_post_probe，ref 55341285）与 S1（ref 55340535）今日已交；
本枪为 A1 的干净对照组（W1 原版，REPLAY_SAFE=0.996，仅去掉 multi-post 模板），
用于回答新 harness 偏移量与 A1 增益归属。

- [x] local_sim_guardrail @0%（3-salt）：LOCAL_SCORE=36.0000 / GO
      （本地 400 cap 口径；真实 MAX_CANDIDATES=2000，回放风险由 REPLAY_SAFE
      0.996 与 8/7 重打 ERROR 76.770 先例共同提示——本枪预期同为超时部分分）
- [x] evaluate_candidate（EXFIL 族，mock 适用）：ast/no_op/smoke 全 PASS，
      mock 3/3 local_pass
- [x] 与 A1 同构：同文件基座、同 MAX_CANDIDATES/PROBE_REPS/MIN_FIRE/
      REPLAY_SAFE=0.996，唯一差异 = 无 multi_plain/multi_bare 模板
- [x] 用户批准：submission_approved.txt（坐标系补齐方案第 3 枪）
- [x] 判线：与 A1/S1 同日对比；A1-W1≫噪声 → A1 方法增益成立，第 4 枪 A2 消融；
      三枪接近 → 转执行链排查（valid/replay/sorting/wrapper）。
