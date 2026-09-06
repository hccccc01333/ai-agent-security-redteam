---
conclusion_id: CONC-0025
framework_id: F010
plan_id: P8
component_set: [C001, C014, C015]
date: 2026-08-10
status: active
---

## 结论（真实网关架构审计：静态池是自设的框，自适应探测才是正路）

- 时间：2026-08-10（读取本地 data/kaggle_evaluation/jed_attack_134815/jed_attack_gateway.py）
- 事实（源码级）：
  1. **提交分数 = 4 行**：gpt_oss_public / gpt_oss_private / gemma_public /
     gemma_private；公榜 = 两模型 public 行之和（推断），私榜同理 → 我们从未
     按模型拆分优化，等于只当“一个总分”玩；
  2. **攻击阶段每模型独立 9000s，跑的是真模型**（RemoteAgent gpt-oss-20b /
     gemma-4）：attack.py 的 env.interact 探测是实时真模型反馈 → W1 的
     运行时 fire 探测才是与 harness 匹配的架构；S 系列静态池是自设的框；
  3. **同组候选分别对 public/private 重放**（每模型每护栏各 9000s）；
     MAX_REPLAY_FINDINGS=2000、每条 ≤32 消息；
  4. **私榜 = 真实包 `aicomp_private_guardrails.persistent_provenance.Guardrail`**
     （entry point persistent_provenance_private），评估时从 /kaggle/input
     安装轮子；本地只有公榜 OptimalGuardrail → 我们 15% 档代理只是同名近似，
     不是真私榜；但“persistent_provenance”这个名字与我们代理的方向一致
     （来源/污染追踪），细节未知；
  5. 本地网关版本超时抛 INVALID_SUBMISSION；官方 8/7 新规则（保留部分分）
     不在该副本中 → 以线上行为为准。
- 推论（框修正）：
  - 目标函数改为：max(gpt_oss_public+gemma_public) 与
    max(gpt_oss_private+gemma_private)；模型分拆、模型特异性模板是真变量；
  - 攻击 = **自适应运行时生成器**（探测 → 选型 → 装填），不是静态候选池；
  - W1（87.93/82.9）就是自适应架构，应作为主干继续深挖，而不是被
    “CONFUSED 私榜保险”降级；
  - EXFIL（16 权重）在宽松型私榜下可直接 80+；persistent_provenance 真私榜
    细节未知 → 双线并存，任何一条都不冻结。
- 失败分类：其他（框架困境：静态池 + 单总分假设 + 自建代理替代真护栏）
- 重开条件：① 找到 aicomp_private_guardrails 轮子（评估输入可遇不可求）；
  ② 自适应 EXFIL 生成器（W1 主干 + 多模板运行时路由）上线；
  ③ 模型拆分候选实验（按 gpt_oss/gemma 分桶，无法直接观测时用
     public 总分差推断）。
