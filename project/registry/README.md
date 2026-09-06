# Experiment Registry — JED Research OS（Frontis-MA1 工程适配）

> 作用：把「散落在聊天/Markdown/终端里的实验状态」固化成机器可读、可追加、可审计的记录。
> 对应论文机制：Experiment Registry + Candidate DAG + Evaluator + 硬 Gate。

## 文件

| 文件 | 内容 |
|------|------|
| `experiments.jsonl` | 逐候选实验记录（一行一个 JSON，append-only，`--replace` 可重写同 id） |
| `submissions.jsonl` | 全部公榜提交明细（由 `submissions_full.csv` 回填，可再生成） |
| `candidate_dag.md` | 候选分支树（防「只在最高分上堆补丁」） |
| `experience.jsonl` | 结构化失败经验：pattern / failure_reason / evidence / ban_condition / reconsider_when |
| `../specs/competition.yaml` | 机器可读任务包：规则/计分/护栏/冻结件/锚点/验证信任度 |

规划前必读 `experience.jsonl`：完全重复 → 禁跑；条件不同 → 说明差异；失败模块的局部子组件 → 允许受限变体。

## Registry CLI（Agent 查询入口，不翻原始 JSONL）

```powershell
python scripts/registry.py status
python scripts/registry.py get w1_probe5_fire65
python scripts/registry.py search --bucket knob_probe
python scripts/registry.py parents w1_probe5_fire65
python scripts/registry.py check --change "<新改动描述>"   # 命中 ban -> 退出码 1
python scripts/registry.py mark w1_probe5_fire65 --status promoted --reason "LB >= parent"
```

## 全量回放裁判（多步族 medium-trust）

```powershell
python scripts/replay_judge.py --budget-s 120 --guardrail optimal --max-replay 200
```

## 本地探索器（Draft 族，并行于提交）

```powershell
python scripts/local_explore.py
```

扫文件读/web 注入页/邮件读消息池，输出 optimal 护栏下真实成交（2026-08-02：23 条 0 成交 → EXP-011）。

## 历史回填（已有 50 条）

```powershell
python scripts/backfill_registry.py
```

把 `submissions_full.csv` 的每个提交映射到变体文件，计算 code_hash、父节点、判定（>= 父分 → promoted），合并进 `experiments.jsonl`。已有富条目（Q5/S2/V5/W1 带评估器数据）只补缺、不覆盖。

## 半自动调度 + 出分同步（阶段四）

```powershell
# 生成下一份 07 合同草案（父节点/假说/门禁自动填；命中经验 BAN 会拒绝提案）
python scripts/propose_next.py --bucket pred_exfil

# 拉最新提交，刷新 submissions.jsonl，自动补记公榜分并给判定（>=父分 -> promoted）
python scripts/sync_submissions.py
```

## 记录字段（experiments.jsonl）

```json
{
  "experiment_id": "W1",
  "registered_at": "2026-08-02T...Z",
  "variant_file": "variants/w1_probe5_fire65.py",
  "parent_id": "Q5",
  "parent_variant": "variants/q5_inj_short.py",
  "operator": "improve",
  "bucket": "knob_probe",
  "hypothesis": {
    "target": "选型严格度",
    "change": "PROBE_REPS 3->5; MIN_FIRE 0.34->0.65",
    "expected_mechanism": "5 样本成本估计更稳 -> 选到更便宜成交模板 -> 同回放预算内候选更多"
  },
  "provenance": {
    "code_hash": "f3c8ff7d...",
    "parent_code_hash": "7c45ecac...",
    "diff_added": 3,
    "diff_removed": 3
  },
  "metrics": {
    "smoke_allow": {"exit": 0, "candidates": "5", "hits": "0", "seconds": 1.0},
    "smoke_optimal": {"exit": 0, "candidates": "5", "hits": "0", "seconds": 1.2},
    "smoke_optimal_s456": {"exit": 0, "candidates": "5", "hits": "0", "seconds": 1.2},
    "validation_trust": "low",
    "public_score": null
  },
  "audits": {"ast": "pass", "no_op": "pass", "smoke_allow": "pass", "smoke_optimal": "pass", "mock_selection": "pass"},
  "decision": {
    "status": "local_pass",
    "submitted": true,
    "submission_ref": "55177036",
    "kernel_version": 71,
    "public_score": null,
    "reason": "deterministic gate passed; awaiting LB"
  }
}
```

## 命令

```powershell
cd "d:\AI数据分析\kaggle比赛\人工智能代理安全——多步工具攻击\project"

# 评估候选（确定性门禁 + 自动登记；--mock 校验选型逻辑；--copy-attack 自动切 attack.py 并还原）
python scripts/evaluate_candidate.py --variant variants\w1_probe5_fire65.py `
    --parent variants\q5_inj_short.py --bucket knob_probe `
    --hypothesis "PROBE_REPS 3->5; MIN_FIRE 0.34->0.65" --mock --copy-attack --validation-trust low

# 提交后补记公榜结果（--replace 更新同 id 行）
python scripts/evaluate_candidate.py --variant variants\w1_probe5_fire65.py `
    --submission-ref 55177036 --kernel-version 71 --public-score 87.795 --replace
```

## 硬规则

- 评估必须由 `evaluate_candidate.py` 确定性执行，不允许 LLM 读日志后主观判定「过了」。
- 一轮实验 = 一个核心假说 = 一个可解释改动主题（`prompts/06` + `prompts/07`）。
- 规划前先查 `experience.jsonl` 的 ban_condition；命中即停。
- 提交只走 `submit_one.ps1`，且必须用户说「提交」；ERROR 即停。
- 登记失败配方（memory/），防止重复烧枪。
