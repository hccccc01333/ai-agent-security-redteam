---
conclusion_id: CONC-0017
framework_id: F010
plan_id: P0-P4
component_set: [C001, C014, C015]
date: 2026-08-08
status: active
---

## 结论（线上归因底座已建：manifest + contrast + 分离审计 + unobservable）

- 时间：2026-08-08 14:50 +08
- 思路 / 方案：F010 Online Attribution Layer；本轮只做不依赖线上数据的部分，
  不提交（今日 3 枪已用，4/5 保留）
- 指标与证据：
  - Submission Manifest 已建并回填 S1/A1/W1（family_mix/router/selector/budget）；
  - Contrast 池 4 版（balanced + DC/DT/DR-heavy）全部 GO，本地 29.65-30.14，
    结构仅 family_mix 不同 → 线上总分差可归因；
  - Family 分离审计：特征向量 between/within=17.7×，bigram=2.27× → SEPARATED；
  - FAILURE_MIX 增加 unobservable：S4 多收件人探针本地 full=0、
    unobservable≈404/500（mock 表达不了多工具调用，分数不再伪装成 full）；
  - mock 定位正式降级为 gate（validity/format/budget/regression），
    不再作 candidate quality ranker；
- 失败分类：无（本地底座完成，等待 S1/A1/W1 回榜这一外部依赖）
- 重开条件：① 三枪任一回榜 → 回填 manifest public_score 并跑第一个归因点；
  ② S1 正常 → 打 S5 balanced；③ S1 掉分 → 打 S2 clean anchor。
